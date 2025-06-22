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
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel

# %%
chat = ChatOllama(model="devstral")
messages = [HumanMessage(content="What model are you?")]

# %%
resp = chat.invoke(messages)

# %%
resp


# %%
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


class WeatherResponse(BaseModel):
    conditions: str


agent = create_react_agent(
    model=chat,
    tools=[get_weather],
    prompt="You are a helpful assistant",
    response_format=WeatherResponse,
)

# Run the agent
resp = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

# %%
resp["messages"]

# %%
