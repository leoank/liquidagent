"""
Simple ChEMBL Similarity Search

A minimal implementation for searching similar compounds in the ChEMBL database.
"""

import asyncio
import logging
import threading
from typing import Any, Dict

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

CHEMBL_BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"


async def search_similar_compounds(
    smiles: str, threshold: int = 100, max_results: int = 20, timeout: int = 20
) -> Dict[str, Any]:
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
    url = f"{CHEMBL_BASE_URL}/similarity/{smiles}/{threshold}?format=json"
    logger.debug(
        f"Searching ChEMBL with parameters: SMILES={smiles}, threshold={threshold}, max_results={max_results}"
    )

    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as session:
            logger.debug(f"Making API request to: {url}")
            async with session.get(url) as resp:
                if resp.status != 200:
                    error_msg = f"ChEMBL API returned status {resp.status}"
                    logger.error(error_msg)
                    return {"error": error_msg}

                data = await resp.json()
                molecules = data.get("molecules", [])

                if not molecules:
                    warning_msg = f"No compounds found with similarity >= {threshold}%"
                    logger.warning(warning_msg)
                    return {"error": warning_msg}

                logger.info(
                    f"Found {len(molecules)} compounds with similarity >= {threshold}%"
                )
                logger.debug(f"Processing up to {max_results} results")

                results = []
                for mol in molecules[:max_results]:
                    chembl_id = mol.get("molecule_chembl_id")
                    canonical_smiles = mol.get("molecule_structures", {}).get(
                        "canonical_smiles"
                    )
                    similarity = mol.get("similarity")
                    name = mol.get("pref_name")

                    if not chembl_id or not canonical_smiles:
                        logger.warning(
                            f"Skipping molecule due to missing required data: {mol.get('molecule_chembl_id', 'Unknown ID')}"
                        )
                        continue

                    results.append(
                        {
                            "chembl_id": chembl_id,
                            "canonical_smiles": canonical_smiles,
                            "similarity": similarity,
                            "name": name,
                        }
                    )
                    logger.debug(
                        f"Added compound {chembl_id} with similarity {similarity}"
                    )

                logger.info(f"Successfully processed {len(results)} compounds")
                return {"results": results, "total_found": len(molecules)}

    except asyncio.TimeoutError:
        error_msg = f"Request timed out after {timeout} seconds"
        logger.error(error_msg)
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {"error": error_msg}


def search_similar_compounds_sync(
    smiles: str, threshold: int = 100, max_results: int = 20
) -> Dict[str, Any]:
    """
    Synchronous wrapper for the async search function.
    """
    logger.debug("Starting synchronous search")
    try:
        result = asyncio.run(search_similar_compounds(smiles, threshold, max_results))
    except RuntimeError:
        result = None

        def run_func():
            nonlocal result
            result = asyncio.run(
                search_similar_compounds(smiles, threshold, max_results)
            )

        thread = threading.Thread(target=run_func)
        thread.start()
        thread.join()
    logger.debug("Completed synchronous search")
    return result


# Example usage
if __name__ == "__main__":
    # Set debug level for more detailed logging during testing
    logger.setLevel(logging.DEBUG)

    # Example: Search for compounds similar to aspirin
    test_smiles = "CC(=O)Oc1ccccc1C(=O)O"  # Aspirin
    hard_smiles = "CN(C)C/C=C/C(=O)Nc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1O[C@@H]1CCOC1"

    # Async usage
    async def test_async():
        logger.info("Testing async search...")
        result = await search_similar_compounds(
            hard_smiles, threshold=90, max_results=5
        )
        # add result of test_smiles
        result_test = await search_similar_compounds(
            test_smiles, threshold=90, max_results=5
        )

        print("Async test smiles :", result_test)
        print("Async hard smiles search :", result)

    # Sync usage
    def test_sync():
        logger.info("Testing sync search...")
        result = search_similar_compounds_sync(hard_smiles, threshold=90, max_results=5)
        print("Sync search results:", result)

    # Run tests
    print("Testing async search...")
    asyncio.run(test_async())

    print("\nTesting sync search...")
    test_sync()
