# Liquid Agent

Liquid Agent is a chemoinformatics-first research agent prototype designed to explore patent space for medicinal chemistry applications. This project is built to test collaboration between cheminformatics experts and AI tool builders, with a goal of evaluating synergies before scaling the team.

## 🧠 Purpose

We are building an agent that can:

- Accept flexible natural language input (e.g., compound, target, property of interest) via an LLM interface to support broader and more intuitive search.
- Retrieve structurally similar compounds from the SureChEMBL database.
- Identify related patents from the USPTO dataset.
- Extract and summarize experimental data (e.g., potency, assays, solubility) from patent documents.
- Analyze structure-activity relationships (SAR) by comparing analog series within patents.
- Identify "hidden" or cryptic compounds disclosed in patents.
- Provide overviews of compound landscapes for a given biological target.

## 🧰 Stack

- Python 3.10+
- [`rdkit`](https://www.rdkit.org/) for molecular similarity and fingerprinting.
- [`langchain`, `langgraph`] (planned) for agentic workflow orchestration.
- [`polars`] for fast dataframe operations.
- [`surechembl`](https://www.ebi.ac.uk/chembl/surechembl) for chemical-patent mappings.
- [`USPTO`](https://developer.uspto.gov/) public patent data with API access via:
  - Sample key: `gJNDuYDHqyCCBNWo54eOktlaLkinpGEF`
  - Reference: [Amazon Bedrock Healthcare/Life Sciences USPTO Agent](https://github.com/aws-samples/amazon-bedrock-agents-healthcare-lifesciences/tree/b4444fa7606f5ba5d6bd4deb84f15817bba9d560/agents_catalog/14-USPTO-search)
-  https://github.com/microsoft/magentic-ui Framework 1
-  https://github.com/microsoft/autogen Framework 2
-  Or without framework ... 




## 🧪 Notebooks

Early experiments live in the `notebooks/` directory:

- `01_explore_langchain.py` — Using LangChain with Ollama backend
- `02_explore_litellm.py` — Streaming output from local model via LiteLLM

## 🔧 CLI

A CLI tool is scaffolded in `src/liquidagent/cli.py` (entry point: `biomimir`) and will be extended to handle:

- Compound input: `biomimir search --smiles "<SMILES>"`
- Target input: `biomimir search --target "<gene/protein>"`

## 📚 Reference

- SureChEMBL paper: [SciFinder to SureChEMBL: Interfacing Chemical Search Tools with Public Patent Data](https://pubs.acs.org/doi/10.1021/acs.jcim.1c00151)
- USPTO integration reference: AWS Bedrock Agent example [14-USPTO-search](https://github.com/aws-samples/amazon-bedrock-agents-healthcare-lifesciences/tree/b4444fa7606f5ba5d6bd4deb84f15817bba9d560/agents_catalog/14-USPTO-search)

## 🧑‍💻 Development Focus

This project is a prototype to test and co-develop agentic workflows for chemistry-aware patent search. The work spans:

- Integrating SureChEMBL compound similarity search.
- Building compound-to-patent mappings using public USPTO datasets.
- Parsing and extracting chemical and experimental data from patent documents.
- Performing SAR (structure-activity relationship) extraction and reasoning.
- Accepting natural language input via an LLM interface to drive agent workflows.
- Creating CLI commands and modular tools that can later compose into a LangGraph-style agent.

This is an opportunity to explore autonomy, creativity, and design in the context of building a deep, domain-specific research agent for early-stage drug discovery.


## Evaluation set

Paired exmaple of extraction from patents and paired exmaples. (from users's end)
