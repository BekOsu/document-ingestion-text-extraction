import logging
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)


def extract_text_ocr(pdf_path: Path, dpi: int = 200) -> str:
    try:
        images = convert_from_path(str(pdf_path), dpi=dpi)
    except Exception as e:
        logger.error(f"Failed to convert PDF to images: {e}")
        raise

    text_parts = []
    for i, image in enumerate(images):
        try:
            page_text = pytesseract.image_to_string(image)
            text_parts.append(page_text)
        except Exception as e:
            logger.warning(f"OCR failed on page {i + 1}: {e}")

    return "\n\n".join(text_parts)