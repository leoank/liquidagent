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
from os import name

from liquidagent.chat_model.base import Tool
from liquidagent.config import (
    LiquidAgentConfig,
    OllamaProviderConfig,
    SupportedModelProviders,
)
from liquidagent.utils import get_chat_model

# %% [markdown]
# Testing out the liquidagent api

# %%
config = LiquidAgentConfig(
    preferred_model=SupportedModelProviders("ollama"),
    ollama=OllamaProviderConfig(
        host="http://karkinos:11434",
        model="devstral",
    ),
)


# %%
def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers

    Args:
      a (int): The first number
      b (int): The second number

    Returns:
      int: The sum of the two numbers
    """

    # The cast is necessary as returned tool call arguments don't always conform exactly to schema
    # E.g. this would prevent "what is 30 + 12" to produce '3012' instead of 42
    return int(a) + int(b)


def subtract_two_numbers(a: int, b: int) -> int:
    """
    Subtract two numbers
    """

    # The cast is necessary as returned tool call arguments don't always conform exactly to schema
    return int(a) - int(b)


# Tools can still be manually defined and passed into chat
subtract_two_numbers_tool = {
    "type": "function",
    "function": {
        "name": "subtract_two_numbers",
        "description": "Subtract two numbers",
        "parameters": {
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {"type": "integer", "description": "The first number"},
                "b": {"type": "integer", "description": "The second number"},
            },
        },
    },
}

available_functions = {
    "add_two_numbers": add_two_numbers,
    "subtract_two_numbers": subtract_two_numbers,
}


# %%
def process_out(resp) -> None:
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


# %%
llm = get_chat_model(config)
llm.bind_tools([add_two_numbers, subtract_two_numbers_tool])
messages = [
    {
        "content": "What is 7 minus 7? Answer this query will available tools",
        "role": "user",
    }
]
resp = llm.invoke(
    messages=messages,
    stream=True,
)
process_out(resp)


# %%
resp = llm.invoke(
    messages=messages,
    stream=True,
)
process_out(resp)

# %%
messages = [
    {
        "content": "What is 7 minus 7? Answer this query will available tools",
        "role": "user",
    }
]
llm.agent(messages, True, available_functions)

# %%
