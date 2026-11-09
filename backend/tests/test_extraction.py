import fitz
import pytest
from docx import Document

from app.services.extraction import extract_text


def test_extract_docx(tmp_path):
    path = tmp_path / "invoice.docx"
    doc = Document()
    doc.add_paragraph("Invoice 2026-001")
    doc.add_paragraph("Total: 420 EUR")
    doc.save(path)
    assert extract_text(path, "docx") == "Invoice 2026-001\nTotal: 420 EUR"


def test_extract_pdf(tmp_path):
    path = tmp_path / "contract.pdf"
    pdf = fitz.open()
    pdf.new_page().insert_text((72, 72), "Contract between A and B")
    pdf.save(path)
    assert "Contract between A and B" in extract_text(path, "pdf")


def test_unsupported_type_raises(tmp_path):
    with pytest.raises(ValueError):
        extract_text(tmp_path / "x.exe", "exe")
