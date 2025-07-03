__all__ = ["logger", "AnthropicChatModel"]

import logging
from collections.abc import Callable, Iterator

from anthropic import Anthropic
from anthropic.types import Message as AnthropicMessage
from anthropic.types import MessageParam, ToolParam
from ollama import Message

from ..config import AnthropicProviderConfig
from .base import ChatModelProtocol, ChatModelResponse, Tool

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AnthropicChatModel(ChatModelProtocol):
    def __init__(self, config: AnthropicProviderConfig) -> None:
        self.client = Anthropic(api_key=config.api_key, base_url=config.base_url)
        self.config = config

    def _convert_messages(self, messages: list[str]) -> list[MessageParam]:
        return messages

    def _convert_tools(self, tools: list[Tool]) -> list[ToolParam]:
        converted_tools = []
        for tool in tools:
            converted_tool: ToolParam = {
                "name": tool["function"]["name"],
                "description": tool["function"]["description"],
                "input_schema": tool["function"]["parameters"],
            }
            converted_tools.append(converted_tool)
        return converted_tools

    def _convert_resp(self, resp: AnthropicMessage) -> ChatModelResponse:
        tool_calls = None
        content = ""

        for content_block in resp.content:
            if content_block.type == "text":
                content += content_block.text
            elif content_block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                tool_calls.append(
                    {
                        "function": {
                            "name": content_block.name,
                            "arguments": content_block.input,
                        }
                    }
                )

        message = Message(role=resp.role, content=content, tool_calls=tool_calls)

        return ChatModelResponse(
            model=resp.model, created_at=str(resp.usage.input_tokens), message=message
        )

    def bind_tools(self, tools: list[Tool]) -> None:
        self.tools = tools

    def invoke(
        self, messages: list = [], stream=False
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        converted_tools = (
            self._convert_tools(self.tools) if hasattr(self, "tools") else None
        )

        resp = self.client.messages.create(
            model=self.config.model,
            max_tokens=1024,
            messages=messages,
            tools=converted_tools,
        )

        if not stream:
            return self._convert_resp(resp)
        else:
            return iter([self._convert_resp(resp)])

    def agent(
        self,
        messages: list = [],
        stream=False,
        available_functions: dict[str, Callable] = {},
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        logger.info(f"Messages len: {len(messages)}")
        response = self.invoke(messages, stream)

        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                if function_to_call := available_functions.get(tool.function.name):
                    if tool.function.arguments == {} or tool.function.arguments is None:
                        continue
                    print("Calling function:", tool.function.name)
                    print("Arguments:", tool.function.arguments)
                    output = function_to_call(**tool.function.arguments)
                else:
                    print("Function", tool.function.name, "not found")
                    output = f"Function {tool.function.name} not found"

                messages.append(
                    {"role": "assistant", "content": response.message.content}
                )
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool.function.name,
                                "content": [{"type": "text", "text": str(output)}],
                            }
                        ],
                    }
                )
                return self.agent(messages, stream, available_functions)
        else:
            print(response.message.content, end="", flush=True)

        return messages

