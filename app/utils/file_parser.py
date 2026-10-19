"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

import io

from docx import Document
from pypdf import PdfReader


def extract_text(filename: str, data: bytes) -> str:
    """Extract plain text from a PDF or DOCX file.

    Args:
        filename: Original file name, used to determine type.
        data: Raw file bytes.

    Returns:
        Extracted text content.

    Raises:
        ValueError: If the file type is not supported.
    """
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(data)
    if lower.endswith(".docx"):
        return _extract_docx(data)
    raise ValueError(f"Unsupported file type: {filename}. Upload a PDF or DOCX file.")


def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    return "\n".join(para.text for para in doc.paragraphs)
