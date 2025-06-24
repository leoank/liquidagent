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
# | default_exp utils

# %%
# | export
from liquidagent.chat_model.base import ChatModelProtocol
from liquidagent.chat_model.ollama import OllamaChatModel
from liquidagent.config import LiquidAgentConfig, SupportedModelProviders

# %% [markdown]
# Defining some utility functions


# %%
# | export
def get_chat_model(
    config: LiquidAgentConfig, provider: str | None = None
) -> ChatModelProtocol:
    """
    Retrieves a chat model based on the provided configuration.

    Parameters
    ----------
    config : LiquidAgentConfig
        The configuration object containing the preferred model and related settings.
    provider : str, optional
        The specific provider to use. Defaults to None.

    Returns
    -------
    ChatModelProtocol
        The instantiated chat model.

    Raises
    ------
    ValueError
        If the preferred model is not supported.
    """
    # Override preferred_model if provider is given
    if provider is not None:
        config.preferred_model = SupportedModelProviders(provider)

    if config.preferred_model == SupportedModelProviders.OLLAMA:
        assert config.ollama is not None
        return OllamaChatModel(config.ollama)

    raise ValueError("chat model not supported")


# %%
# | export
def process_out(resp, available_functions, messages) -> None:
    for chunk in resp:
        if chunk.message.tool_calls:
            # There may be multiple tool calls in the response
            for tool in chunk.message.tool_calls:
                # Ensure the function is available, and then call it
                if function_to_call := available_functions.get(tool.function.name):
                    print("Calling function:", tool.function.name)
                    print("Arguments:", tool.function.arguments)
                    output = function_to_call(**tool.function.arguments)
                    print("Function output:", output)
                else:
                    print("Function", tool.function.name, "not found")

                # Add the function response to messages for the model to use
                messages.append(chunk.message)
                messages.append(
                    {"role": "tool", "content": str(output), "name": tool.function.name}
                )
        else:
            print(chunk.message.content, end="", flush=True)
            return messages


# %%
# | hide
import nbdev  # noqa

nbdev.nbdev_export()

# %%
