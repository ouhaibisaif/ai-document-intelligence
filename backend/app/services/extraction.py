from pathlib import Path

import fitz
from docx import Document as DocxDocument
from PIL import Image

from app.utils.text import clean_text


def extract_text(file_path: Path, file_type: str) -> str:
    if file_type == "pdf":
        return clean_text(_extract_pdf(file_path))
    if file_type == "docx":
        return clean_text(_extract_docx(file_path))
    if file_type in {"png", "jpg", "jpeg"}:
        return clean_text(_extract_image(file_path))
    raise ValueError(f"Unsupported file type: {file_type}")


def _extract_pdf(file_path: Path) -> str:
    parts: list[str] = []
    with fitz.open(file_path) as pdf:
        for page in pdf:
            parts.append(page.get_text())
    return "\n".join(parts)


def _extract_docx(file_path: Path) -> str:
    doc = DocxDocument(file_path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def _extract_image(file_path: Path) -> str:
    try:
        import pytesseract
    except ImportError:
        return ""

    with Image.open(file_path) as image:
        return pytesseract.image_to_string(image)
