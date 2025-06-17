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
from litellm import completion

response = completion(
    model="ollama/devstral",
    messages=[{"content": "respond in 20 words. who are you?", "role": "user"}],
    api_base="http://localhost:11434",
    stream=True,
)
print(response)
for chunk in response:
    print(chunk["choices"][0]["delta"])
