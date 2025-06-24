__all__ = ["logger", "OpenAIChatModel"]

import json
import logging
from collections.abc import Callable, Iterator
from uuid import uuid4

from ollama import Message
from openai import OpenAI
from openai.types.chat import ChatCompletion as OpenAIChatCompletion

from ..config import OpenAIProviderConfig
from .base import ChatModelProtocol, ChatModelResponse, Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# OpenAI chat model
class OpenAIChatModel(ChatModelProtocol):
    def __init__(self, config: OpenAIProviderConfig) -> None:
        self.client = OpenAI(api_key=config.api_key)
        self.config = config

    def _convert_messages(self, messages: list[str]) -> list[str]:
        return messages

    def _convert_tools(self, tools: list) -> list:
        return tools

    def _fix_tool_call_message(self, message: Message) -> dict:
        message_dict = message.model_dump()
        fixed_tool_calls = []
        for tool_call in message.tool_calls:
            fixed_arguments = str(tool_call.function.arguments)
            tool_call = tool_call.model_dump()
            tool_call["id"] = str(uuid4())
            tool_call["type"] = "function"
            tool_call["function"]["arguments"] = fixed_arguments
            fixed_tool_calls.append(tool_call)
        message_dict["tool_calls"] = fixed_tool_calls
        return message_dict

    def _parse_oai_argument(self, arguments: str | None) -> dict:
        if arguments == "" or arguments is None:
            return {}
        else:
            return json.loads(arguments)

    def _convert_resp(
        self, resp: OpenAIChatCompletion, stream: bool = False
    ) -> ChatModelResponse:
        # logger.info(f"OpenAI message: {resp}")
        if stream:
            oai_message = resp.choices[0].delta
        else:
            oai_message = resp.choices[0].message
        # try parsing function arguments
        message = Message(
            role=oai_message.role,
            content=oai_message.content,
            tool_calls=[
                {
                    "function": {
                        "name": tool.function.name,
                        "arguments": self._parse_oai_argument(tool.function.arguments),
                    }
                }
                for tool in oai_message.tool_calls
            ],
        )
        return ChatModelResponse(
            model=resp.model, created_at=str(resp.created), message=message
        )

    def bind_tools(self, tools: list[Tool]) -> None:
        self.tools = tools

    def invoke(
        self, messages: list = [], stream=False
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        resp = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=stream,
            tools=self.tools,
            tool_choice="auto",
        )
        if not stream:
            resp = self._convert_resp(resp, stream)
            return resp
        else:
            return map(lambda chunk: self._convert_resp(chunk, stream), resp)

    def agent(
        self,
        messages: list = [],
        stream=False,
        available_functions: dict[str, Callable] = {},
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        logger.info(f"Messages len: {len(messages)}")
        stream = False
        response = self.invoke(messages, stream)
        if response.message.tool_calls:
            # There may be multiple tool calls in the response
            for tool in response.message.tool_calls:
                # Ensure the function is available, and then call it
                if function_to_call := available_functions.get(tool.function.name):
                    if tool.function.arguments == {} or tool.function.arguments is None:
                        continue
                    print("Calling function:", tool.function.name)
                    print("Arguments:", tool.function.arguments)
                    output = function_to_call(**tool.function.arguments)
                    # print("Function output:", output)
                else:
                    print("Function", tool.function.name, "not found")

                # Add the function response to messages for the model to use
                fixed_message = self._fix_tool_call_message(response.message)
                messages.append(fixed_message)
                messages.append(
                    {
                        "role": "tool",
                        "content": str(output),
                        "name": tool.function.name,
                        "tool_call_id": fixed_message["tool_calls"][0]["id"],
                    }
                )
                return self.agent(messages, True, available_functions)
        else:
            print(response.message.content, end="", flush=True)
        return messages
