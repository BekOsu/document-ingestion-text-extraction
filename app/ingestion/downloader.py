import logging
import time
import hashlib
from pathlib import Path
from urllib.parse import urlparse
import requests

from app.config import RAW_DIR, DOWNLOAD_TIMEOUT, MAX_RETRIES

logger = logging.getLogger(__name__)


def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    if not name or not name.endswith(".pdf"):
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        name = f"document_{url_hash}.pdf"
    return name


def validate_pdf_url(url: str, timeout: int = 10) -> bool:
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        content_type = resp.headers.get("Content-Type", "")
        return "application/pdf" in content_type or url.lower().endswith(".pdf")
    except requests.RequestException:
        return False


def download_pdf(url: str, output_dir: Path = RAW_DIR) -> Path | None:
    filename = get_filename_from_url(url)
    output_path = output_dir / filename

    if output_path.exists():
        logger.info(f"Already downloaded: {filename}")
        return output_path

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
            resp.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Downloaded: {filename}")
            return output_path

        except requests.RequestException as e:
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(wait_time)

    logger.error(f"Failed to download after {MAX_RETRIES} attempts: {url}")
    return None


def download_batch(urls: list[str]) -> list[tuple[str, Path | None]]:
    results = []
    for url in urls:
        path = download_pdf(url)
        results.append((url, path))
    return results