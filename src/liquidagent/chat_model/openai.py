__all__ = ["logger", "OpenAIChatModel"]

import json
import logging
from collections.abc import Callable, Iterator

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

    def _parse_oai_argument(self, arguments: str | None) -> dict:
        if arguments == "" or None:
            return {}
        else:
            json.loads(arguments)

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
        self.tools = self._convert_tools(tools)

    def invoke(
        self, messages: list = [], stream=False
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        resp = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            stream=stream,
            tools=self.tools,
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
        response = self.invoke(messages, stream)
        if stream:
            merged_content = []
            for chunk in response:
                if chunk.message.tool_calls:
                    # There may be multiple tool calls in the response
                    for tool in chunk.message.tool_calls:
                        # Ensure the function is available, and then call it
                        if function_to_call := available_functions.get(
                            tool.function.name
                        ):
                            print("Calling function:", tool.function.name)
                            print("Arguments:", tool.function.arguments)
                            output = function_to_call(**tool.function.arguments)
                            # print("Function output:", output)
                        else:
                            print("Function", tool.function.name, "not found")

                        # Add the function response to messages for the model to use
                        messages.append(chunk.message)
                        messages.append(
                            {
                                "role": "tool",
                                "content": str(output),
                                "name": tool.function.name,
                            }
                        )
                        return self.agent(messages, True, available_functions)
                else:
                    merged_content.append(chunk.message.content)
                    print(chunk.message.content, end="", flush=True)
            merged_content = "".join(merged_content)
            messages.append(
                {
                    "role": "assistant",
                    "content": merged_content,
                }
            )
            return messages
