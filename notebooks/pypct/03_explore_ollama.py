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
from ollama import chat

resp = chat(
    model="devstral",
    messages=[{"content": "respond in 20 words. who are you?", "role": "user"}],
    stream=True,
)
for chunk in resp:
    print(chunk.message.content, end="", flush=True)
