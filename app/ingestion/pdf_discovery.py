import logging
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def extract_pdf_links(page_url: str, timeout: int = 15) -> list[str]:
    try:
        resp = requests.get(page_url, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {page_url}: {e}")
        return []

    soup = BeautifulSoup(resp.content, "html.parser")
    pdf_links = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if href.lower().endswith(".pdf"):
            full_url = urljoin(page_url, href)
            pdf_links.append(full_url)

    logger.info(f"Found {len(pdf_links)} PDF links on {page_url}")
    return list(set(pdf_links))


def discover_pdfs_from_pages(page_urls: list[str]) -> list[dict]:
    results = []
    for url in page_urls:
        pdf_links = extract_pdf_links(url)
        for pdf_url in pdf_links:
            results.append({
                "source_type": "web_page",
                "source_url": url,
                "pdf_url": pdf_url,
            })
    return results