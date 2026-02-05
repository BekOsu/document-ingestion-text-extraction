import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ENCODINGS = ["utf-8", "latin-1", "cp1252"]


def extract_text_from_txt(file_path: Path) -> dict:
    result = {
        "file_name": file_path.name,
        "page_count": 1,
        "extraction_method": "plaintext",
        "extracted_text": None,
        "success": False,
    }

    for encoding in ENCODINGS:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                text = f.read().strip()

            if text:
                result["extracted_text"] = text
                result["success"] = True
                logger.info(f"Read {file_path.name} with {encoding} encoding")
            else:
                logger.warning(f"Empty file: {file_path.name}")

            return result

        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Failed to read {file_path.name}: {e}")
            return result

    logger.error(f"Could not decode {file_path.name} with any encoding")
    return result