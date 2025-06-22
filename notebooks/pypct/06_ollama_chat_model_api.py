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
from collections.abc import Callable, Iterator

from ollama import ChatResponse as OllamaChatResponse
from ollama import Client

from liquidagent.chat_model.base import ChatModelProtocol, ChatModelResponse, Tool
from liquidagent.config import OllamaProviderConfig

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
        self, messages=[], stream=False, available_functions: dict[str, Callable] = {}
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        response = self.invoke(messages, stream)
        if stream:
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
                            print("Function output:", output)
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
                        self.agent(messages, stream, available_functions)
                else:
                    print(chunk.message.content, end="", flush=True)


# %%
# | hide
import nbdev  # noqa

nbdev.nbdev_export()

# %%
