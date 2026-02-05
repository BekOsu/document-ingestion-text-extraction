import logging
from pathlib import Path

from app.extraction.text_extractor import extract_text_from_pdf
from app.extraction.docx_extractor import extract_text_from_docx
from app.extraction.txt_extractor import extract_text_from_txt
from app.extraction.image_extractor import extract_text_from_image

logger = logging.getLogger(__name__)

EXTRACTORS = {
    ".pdf": extract_text_from_pdf,
    ".docx": extract_text_from_docx,
    ".txt": extract_text_from_txt,
    ".png": extract_text_from_image,
    ".jpg": extract_text_from_image,
    ".jpeg": extract_text_from_image,
    ".tiff": extract_text_from_image,
    ".bmp": extract_text_from_image,
}


def extract_text(file_path: Path) -> dict:
    ext = file_path.suffix.lower()

    if ext not in EXTRACTORS:
        logger.error(f"Unsupported file type: {ext}")
        return {
            "file_name": file_path.name,
            "page_count": None,
            "extraction_method": None,
            "extracted_text": None,
            "success": False,
        }

    extractor = EXTRACTORS[ext]
    return extractor(file_path)


def get_supported_extensions() -> list[str]:
    return list(EXTRACTORS.keys())