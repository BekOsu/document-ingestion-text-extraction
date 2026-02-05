import argparse
import logging
import sys
from pathlib import Path

from app.config import RAW_DIR, LOG_LEVEL, LOGS_DIR
from app.ingestion.url_sources import load_urls_from_file, search_pdfs
from app.ingestion.pdf_discovery import discover_pdfs_from_pages
from app.ingestion.downloader import download_pdf
from app.extraction.extractor import extract_text, get_supported_extensions
from app.export.exporter import export_to_json, export_to_csv

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def process_local_files(paths: list[str]) -> list[dict]:
    results = []
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            logger.warning(f"File not found: {path}")
            continue

        result = extract_text(path)
        result["source_type"] = "local"
        result["source_url"] = None
        result["pdf_url"] = None
        results.append(result)

    return results


def process_urls(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        file_path = download_pdf(url)
        if not file_path:
            continue

        result = extract_text(file_path)
        result["source_type"] = "url"
        result["source_url"] = url
        result["pdf_url"] = url
        results.append(result)

    return results


def process_web_pages(page_urls: list[str]) -> list[dict]:
    discoveries = discover_pdfs_from_pages(page_urls)
    results = []

    for item in discoveries:
        file_path = download_pdf(item["pdf_url"])
        if not file_path:
            continue

        result = extract_text(file_path)
        result["source_type"] = item["source_type"]
        result["source_url"] = item["source_url"]
        result["pdf_url"] = item["pdf_url"]
        results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(description="Document ingestion and text extraction")
    parser.add_argument("--files", nargs="+", help="Local file paths to process")
    parser.add_argument("--urls", nargs="+", help="Direct URLs to documents")
    parser.add_argument("--url-file", help="File containing URLs (one per line)")
    parser.add_argument("--pages", nargs="+", help="Web pages to scan for PDF links")
    parser.add_argument("--search", help="Search query for PDF discovery")
    parser.add_argument("--output", choices=["json", "csv", "both"], default="both")

    args = parser.parse_args()

    if not any([args.files, args.urls, args.url_file, args.pages, args.search]):
        parser.print_help()
        sys.exit(1)

    all_results = []

    if args.files:
        logger.info(f"Processing {len(args.files)} local files")
        all_results.extend(process_local_files(args.files))

    if args.urls:
        logger.info(f"Processing {len(args.urls)} URLs")
        all_results.extend(process_urls(args.urls))

    if args.url_file:
        urls = load_urls_from_file(args.url_file)
        logger.info(f"Processing {len(urls)} URLs from file")
        all_results.extend(process_urls(urls))

    if args.pages:
        logger.info(f"Scanning {len(args.pages)} web pages for documents")
        all_results.extend(process_web_pages(args.pages))

    if args.search:
        urls = search_pdfs(args.search)
        logger.info(f"Processing {len(urls)} search results")
        all_results.extend(process_urls(urls))

    if not all_results:
        logger.warning("No documents processed")
        sys.exit(0)

    if args.output in ("json", "both"):
        export_to_json(all_results)

    if args.output in ("csv", "both"):
        export_to_csv(all_results)

    logger.info(f"Processed {len(all_results)} documents")
    successful = sum(1 for r in all_results if r.get("success"))
    logger.info(f"Successful extractions: {successful}/{len(all_results)}")


if __name__ == "__main__":
    main()