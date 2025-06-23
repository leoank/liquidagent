"""Surechembl search tool."""

import logging
from typing import Any, Dict

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SURECHEMBL_BASE_URL = "https://surechembl.org/api/"


def get_chemical_id_from_smiles(smiles: str) -> str:
    """
    Retrieves the chemical ID from SureChEMBL given a SMILES string.

    Args:
        smiles (str): The SMILES string of the chemical.

    Returns:
        str: The chemical ID if found, otherwise an error message.
    """
    logger.debug(f"Searching SureChEMBL for chemical id: SMILES={smiles}")
    resp = requests.post(
        SURECHEMBL_BASE_URL + "chemical/smiles/",
        headers={"Accept": "application/json"},
        params={"smiles": smiles},
    )
    if resp.status_code != 200:
        error_msg = f"SureChEMBL API returned status {resp.status_code}"
        logger.error(error_msg)
        return {"error": error_msg}
    data = resp.json()
    logger.debug(f"Data returned from surechembl: {data}")
    chemical_id = data["data"][smiles]["chemical_id"]
    return chemical_id


def get_patent_ids_from_chemical_ids(chemical_id_list: list[str]) -> list[str]:
    """
    Retrieves patent IDs from SureChEMBL given a list of chemical IDs.

    Args:
        chemical_id_list (list[str]): A list of chemical IDs.

    Returns:
        list[str]: A list of patent IDs.
    """
    logger.debug(
        f"Searching SureChEMBL for patents using chemical ids: {chemical_id_list}"
    )
    resp = requests.post(
        SURECHEMBL_BASE_URL + "search/documents_for_structures",
        headers={"Accept": "application/json"},
        params={"chemicalIds": chemical_id_list, "page": "1", "itemsPerPage": "10"},
    )

    if resp.status_code != 200:
        error_msg = f"SureChEMBL API returned status {resp.status_code}"
        logger.error(error_msg)
        return {"error": error_msg}
    data = resp.json()
    logger.debug(f"Data returned from surechembl: {data}")
    document_list = data["data"]["results"]["documents"]
    document_id_list = []
    for doc in document_list:
        document_id_list.append(doc["docId"])
    return document_id_list


def get_patent_content_from_patent_id(patent_id: str) -> dict:
    """
    Retrieves patent content from SureChEMBL given a patent ID.

    Args:
        patent_id (str): The patent ID.

    Returns:
        dict: A dictionary containing the patent's abstracts, descriptions, and claim responses.
    """
    logger.debug(f"Searching SureChEMBL for patents using patent id: {patent_id}")
    resp = requests.get(
        SURECHEMBL_BASE_URL + f"document/{patent_id}/contents",
        headers={"Accept": "application/json"},
    )
    if resp.status_code != 200:
        error_msg = f"SureChEMBL API returned status {resp.status_code}"
        logger.error(error_msg)
        return {"error": error_msg}
    data = resp.json()
    logger.debug(f"Data returned from surechembl: {data}")

    abstracts = data["data"]["contents"]["patentDocument"]["abstracts"]
    descriptions = data["data"]["contents"]["patentDocument"]["descriptions"]
    claim_responses = data["data"]["contents"]["patentDocument"]["claimResponses"]
    return {
        "abstracts": abstracts,
        "descriptions": descriptions,
        "claim_responses": claim_responses,
    }


def get_patents_from_smiles(smiles: str) -> list[dict]:
    """
    Retrieves patents from SureChEMBL given a SMILES string.

    Args:
        smiles (str): The SMILES string of the chemical.

    Returns:
        list[dict]: A list of dictionaries, each containing the content of a patent.
    """
    logger.debug(f"Searching SureChEMBL for patents using smiles: {smiles}")
    chem_id = get_chemical_id_from_smiles(smiles)
    patent_id_list = get_patent_ids_from_chemical_ids([chem_id])
    patents = []
    for patent_id in patent_id_list:
        patents.append(get_patent_content_from_patent_id(patent_id))

    return patents


# Example usage
if __name__ == "__main__":
    # Set debug level for more detailed logging during testing
    logger.setLevel(logging.DEBUG)

    # Example: Search for compounds similar to aspirin
    test_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    hard_smiles = "CN(C)C/C=C/C(=O)Nc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1O[C@@H]1CCOC1"

    def test_get_chemical_id_from_smiles_aspirin():
        logger.info("Testing aspirin for chemical id search...")
        result = get_chemical_id_from_smiles(test_smiles)
        print("Aspirin test smiles :", result)

    test_get_chemical_id_from_smiles_aspirin()

    # Example: Chemical Id
    chem_id = "1353"  # Aspirin

    def test_get_patent_ids_from_chemical_ids():
        logger.info("Testing aspirin for document id search...")
        result = get_patent_ids_from_chemical_ids([chem_id])
        print("Patent document ids for Asprin :", result)

    test_get_patent_ids_from_chemical_ids()

    # Example: Patent Id
    patent_id = "US-20180037843-A1"

    def test_get_patent_content_from_patent_id():
        logger.info("Testing get patent content search...")
        result = get_patent_content_from_patent_id(patent_id)
        print("Patent document content:", result)

    test_get_patent_content_from_patent_id()
