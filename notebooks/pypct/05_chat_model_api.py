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
# | default_exp chat_model/base

# %%
# | export
from abc import abstractmethod
from collections.abc import Callable, Iterator
from typing import Protocol

from ollama import ChatResponse as OllamaChatResponse
from ollama import Tool as OllamaTool

from liquidagent.config import LiquidAgentConfig

# %% [markdown]
# There are multiple ways of accessing a chat model from different vendors.
# We don't want our implementation to depend on a specific vendor.
# So we define a protocol that defines the interface for a chat model.


# %%
# | export
class Tool(OllamaTool):
    pass


class ChatModelResponse(OllamaChatResponse):
    pass


class ChatModelProtocol(Protocol):
    @abstractmethod
    def bind_tools(self, tools: list[Tool | Callable]) -> None:
        self.tools = tools
        raise NotImplementedError

    @abstractmethod
    def invoke(
        self, messages=[], stream: bool = False
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        raise NotImplementedError

    @abstractmethod
    def agent(
        self,
        messages=[],
        stream=False,
        available_functions: dict[str, Callable | Tool] = {},
    ) -> ChatModelResponse | Iterator[ChatModelResponse]:
        raise NotImplementedError


# %%
def get_chat_model(
    config: LiquidAgentConfig, provider: str | None = None
) -> ChatModelProtocol:
    pass


# %%
# | hide
import nbdev  # noqa

nbdev.nbdev_export()

# %%
