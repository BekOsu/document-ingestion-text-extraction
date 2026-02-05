import logging
from pathlib import Path
from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage

from app.extraction.ocr import extract_text_ocr

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 50


def get_page_count(pdf_path: Path) -> int:
    try:
        with open(pdf_path, "rb") as f:
            return sum(1 for _ in PDFPage.get_pages(f))
    except Exception:
        return 0


def extract_text_from_pdf(pdf_path: Path) -> dict:
    result = {
        "file_name": pdf_path.name,
        "page_count": get_page_count(pdf_path),
        "extraction_method": None,
        "extracted_text": None,
        "success": False,
    }

    try:
        text = extract_text(str(pdf_path))
        text = text.strip() if text else ""

        if len(text) >= MIN_TEXT_LENGTH:
            result["extraction_method"] = "pdfminer"
            result["extracted_text"] = text
            result["success"] = True
            logger.info(f"Extracted text from {pdf_path.name} using pdfminer")
            return result
    except Exception as e:
        logger.warning(f"pdfminer failed for {pdf_path.name}: {e}")

    try:
        text = extract_text_ocr(pdf_path)
        if text and len(text) >= MIN_TEXT_LENGTH:
            result["extraction_method"] = "ocr"
            result["extracted_text"] = text
            result["success"] = True
            logger.info(f"Extracted text from {pdf_path.name} using OCR")
            return result
    except Exception as e:
        logger.warning(f"OCR failed for {pdf_path.name}: {e}")

    logger.error(f"All extraction methods failed for {pdf_path.name}")
    return result