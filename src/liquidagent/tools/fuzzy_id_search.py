"""Common name search tool."""

import logging
from typing import Any, Dict

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PUBCHEM_BASE_URL = "https://cactus.nci.nih.gov/chemical/structure/"


def get_smiles_from_identifier(compound_identifier: str) -> str:
    """
    Retrieves the SMILES for given compound name.

    Args:
        compound_identifier (str): Any chemical compound identifier.

    Returns:
        smiles: The chemical SMILES if found, otherwise an error message.
    """
    logger.debug(f"Searching for compound identifier: {compound_identifier}")
    resp = requests.post(
        PUBCHEM_BASE_URL + f"{compound_identifier}/smiles",
    )
    if resp.status_code != 200:
        error_msg = f"API returned status {resp.status_code}"
        logger.error(error_msg)
        return {"error": error_msg}
    data = resp.text
    logger.debug(f"Data returned from API: {data}")
    return data


get_smiles_from_identifier_tool = {
    "type": "function",
    "function": {
        "name": "get_smiles_from_identifier",
        "description": "Retrieves the SMILES for a given compound identifier. The compound can be InChI/InChIKey, Chemical name (IUPAC or common), CAS registry number, PubChem CID or ChemSpider ID",
        "parameters": {
            "type": "object",
            "required": ["compound_identifier"],
            "properties": {
                "compound_identifier": {
                    "type": "string",
                    "description": "Any chemical compound identifier.",
                },
            },
        },
    },
}
