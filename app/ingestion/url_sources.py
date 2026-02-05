import logging
from typing import Optional
import requests

from app.config import GOOGLE_API_KEY, GOOGLE_CSE_ID

logger = logging.getLogger(__name__)


def load_urls_from_file(filepath: str) -> list[str]:
    with open(filepath, "r") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    logger.info(f"Loaded {len(urls)} URLs from {filepath}")
    return urls


def search_pdfs(query: str, num_results: int = 10) -> list[str]:
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        logger.warning("Google API credentials not configured")
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": f"{query} filetype:pdf",
        "num": min(num_results, 10),
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = [item["link"] for item in data.get("items", [])]
        logger.info(f"Found {len(results)} PDFs for query: {query}")
        return results
    except requests.RequestException as e:
        logger.error(f"Search failed: {e}")
        return []