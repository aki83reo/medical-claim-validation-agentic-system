# app/utils/pdf_utils.py
from pathlib import Path
from pypdf import PdfReader

def read_pdf_text(path: str) -> str:
    """Extract text from a PDF."""
    p = Path(path)
    if not p.exists():
        print(f"[read_pdf_text] File not found: {path}")
        return ""

    reader = PdfReader(str(p))
    texts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        texts.append(txt)
    return "\n".join(texts)
