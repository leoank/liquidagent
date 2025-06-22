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
# | default_exp config

# %%
# | export
from enum import StrEnum, auto

from pydantic import BaseModel

# %% [markdown]
# Let's start with building the application configuration utilities.
# We need classes to configure our models and logging functionality.
# Nothing fancy here. Just some pydantic classes and an Enum for supported model providers.


# %%
# | export
class SupportedModelProviders(StrEnum):
    """Supported model providers."""

    OLLAMA = auto()
    OPENAI = auto()
    ANTHROPIC = auto()
    BEDROCK = auto()


# %%
# | export
class OllamaProviderConfig(BaseModel):
    """Configuration for Ollama models."""

    host: str
    model: str


# %%
# | export
class OpenAIProviderConfig(BaseModel):
    """Configuration for OpenAI models."""

    pass


# %%
# | export
class AnthropicProviderConfig(BaseModel):
    """Configuration for Anthropic models."""

    pass


# %%
# | export
class BedrockProviderConfig(BaseModel):
    """Configuration for Bedrock models."""

    pass


# %%
# | export
class LoggingConfig(BaseModel):
    """Configuration for logging."""

    logfile_path: str = ""


# %%
# | export
class LiquidAgentConfig(BaseModel):
    """Configuration for the Liquid Agent."""

    preferred_model: SupportedModelProviders
    ollama: OllamaProviderConfig | None = None
    openai: OpenAIProviderConfig | None = None
    anthropic: AnthropicProviderConfig | None = None
    bedrock: BedrockProviderConfig | None = None
    logger: LoggingConfig | None = None


# %%
# | hide
import nbdev  # noqa

nbdev.nbdev_export()

# %%
