# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# | default_exp chat_model/ollama

# %%
# | export
import logging
from collections.abc import Callable, Iterator

from ollama import ChatResponse as OllamaChatResponse
from ollama import Client

from liquidagent.chat_model.base import ChatModelProtocol, ChatModelResponse, Tool
from liquidagent.config import OllamaProviderConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# %% [markdown]
# Adding the implementation for Ollama model


# %%
# | export
# Ollama chat model
class OllamaChatModel(ChatModelProtocol):
    def __init__(self, config: OllamaProviderConfig) -> None:
        self.client = Client()
        self.config = config

    def _convert_messages(self, messages: list[str]) -> list[str]:
        return messages

    def _convert_resp(self, resp: OllamaChatResponse) -> ChatModelResponse:
        return ChatModelResponse.model_validate(resp, from_attributes=True)

    def bind_tools(self, tools: list[Tool | Callable]) -> None:
        self.tools = tools

    def invoke(
        self, messages=[], stream=False
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        messages = self._convert_messages(messages)
        resp = self.client.chat(
            model=self.config.model, messages=messages, stream=stream, tools=self.tools
        )
        if not stream:
            resp = self._convert_resp(resp)
            return resp
        else:
            return map(lambda chunk: self._convert_resp(chunk), resp)

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
                            #print("Function output:", output)
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


# %%
# | hide
import nbdev  # noqa

nbdev.nbdev_export()

# %%
