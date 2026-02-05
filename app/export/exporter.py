import csv
import json
import logging
from pathlib import Path
from datetime import datetime

from app.config import PROCESSED_DIR

logger = logging.getLogger(__name__)


def export_to_json(records: list[dict], filename: str = None) -> Path:
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extraction_{timestamp}.json"

    output_path = PROCESSED_DIR / filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    logger.info(f"Exported {len(records)} records to {output_path}")
    return output_path


def export_to_csv(records: list[dict], filename: str = None) -> Path:
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extraction_{timestamp}.csv"

    output_path = PROCESSED_DIR / filename

    if not records:
        logger.warning("No records to export")
        return output_path

    fieldnames = [
        "source_type",
        "source_url",
        "pdf_url",
        "file_name",
        "page_count",
        "extraction_method",
        "extracted_text",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    logger.info(f"Exported {len(records)} records to {output_path}")
    return output_path