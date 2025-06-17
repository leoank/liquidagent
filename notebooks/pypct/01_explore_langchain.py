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

# %%
chat = ChatOllama(model="devstral")
messages = [HumanMessage(content="What model are you?")]

# %%
resp = chat.invoke(messages)

# %%
resp

# %%
