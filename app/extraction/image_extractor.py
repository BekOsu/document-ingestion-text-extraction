import logging
from pathlib import Path
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


def extract_text_from_image(file_path: Path) -> dict:
    result = {
        "file_name": file_path.name,
        "page_count": 1,
        "extraction_method": "ocr",
        "extracted_text": None,
        "success": False,
    }

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        logger.error(f"Unsupported image format: {file_path.suffix}")
        return result

    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        text = text.strip()

        if text:
            result["extracted_text"] = text
            result["success"] = True
            logger.info(f"Extracted text from {file_path.name}")
        else:
            logger.warning(f"No text found in {file_path.name}")

    except Exception as e:
        logger.error(f"Failed to extract from {file_path.name}: {e}")

    return result