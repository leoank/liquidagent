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
from liquidagent.config import (
    LiquidAgentConfig,
    OllamaProviderConfig,
    SupportedModelProviders,
)
from liquidagent.tools.simple_chembl_search import search_similar_compounds_sync
from liquidagent.tools.surechembl_search import get_patents_from_smiles
from liquidagent.utils import get_chat_model, process_out

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
# Tools can be manually defined and passed into chat

"""
Search ChEMBL for compounds similar to the input SMILES.

Args:
    smiles: SMILES string of the compound to search for
    threshold: Similarity threshold (0-100, default 100 for exact match)
    max_results: Max number of results to return (default 20)
    timeout: Request timeout in seconds

Returns:
    Dictionary containing:
    - results: List of compounds with ChEMBL IDs, SMILES, similarity scores
    - total_found: Total number of compounds found
    - error: Error message if search failed
"""
search_similar_compounds_tools = {
    "type": "function",
    "function": {
        "name": "search_similar_chemical_compounds",
        "description": "Search ChEMBL for compounds similar to the input SMILES",
        "parameters": {
            "type": "object",
            "required": ["smiles"],
            "properties": {
                "smiles": {
                    "type": "string",
                    "description": "SMILES string of the compound to search for",
                },
            },
        },
    },
}
get_patents_from_smiles_tool = {
    "type": "function",
    "function": {
        "name": "get_patents_from_smiles",
        "description": "Search SureChEMBL for patents using the input SMILES",
        "parameters": {
            "type": "object",
            "required": ["smiles"],
            "properties": {
                "smiles": {
                    "type": "string",
                    "description": "SMILES string of the compound to retrieve patents for",
                },
            },
        },
    },
}

available_functions = {
    "get_patents_from_smiles": get_patents_from_smiles,
}


# %%
llm = get_chat_model(config)
llm.bind_tools([get_patents_from_smiles])
system_prompt = """
You are a specialized assistant who can help users retrieve patent information for a given chemical compound using the tools available to you.
After retrieving patents, only summarize chemically relevant patents for the user
"""
messages = [
    {
        "content": system_prompt,
        "role": "system",
    },
    {
        "content": "Search patents for the chemical compound CC(=O)OC1=CC=CC=C1C(=O)O",
        "role": "user",
    },
]

# %%
resp_messages = llm.agent(messages, True, available_functions)

# %%
