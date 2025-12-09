# app/agents/claim_extraction_agent.py
import re

from app.utils.pdf_utils import read_pdf_text


NAME_PATTERNS = [
    re.compile(r"Patient Name[:\-]\s*(.+)", re.IGNORECASE),
    re.compile(r"Member Name[:\-]\s*(.+)", re.IGNORECASE),
    re.compile(r"Name[:\-]\s*(.+)", re.IGNORECASE),
]

DISEASE_PATTERNS = [
    re.compile(r"(?:Disease|Diagnosis|Primary Diagnosis)[:\-]\s*(.+)", re.IGNORECASE),
    re.compile(r"Diagnosed with[:\-]\s*(.+)", re.IGNORECASE),
]

AMOUNT_PATTERNS = [
    re.compile(
        r"(?:Total\s+(?:Claim(?:ed)?|Bill|Amount)|Total Claimed Amount)[:\-]?\s*([₹$]?\s?[\d,]+(?:\.\d{1,2})?)",
        re.IGNORECASE,
    ),
    re.compile(r"Total Bill Amount[:\-]?\s*([₹$]?\s?[\d,]+(?:\.\d{1,2})?)", re.IGNORECASE),
]


def _extract_field(patterns, text: str, default: str = "Unknown") -> str:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            value = match.group(match.lastindex or 1).strip()
            return re.sub(r"\s+", " ", value)
    return default


class ClaimExtractionAgent:
    """Parses claim PDFs and extracts disease, amount, name."""

    def extract_claim(self, state: dict) -> dict:
        docs = state.get("docs", [])
        print(f"[extract_claim] Extracting from: {docs}")

        if len(docs) != 2:
            print("[extract_claim] ERROR: Expected 2 PDFs.")
            return {"extracted": {}}

        discharge_pdf, claim_pdf = docs

        text1 = read_pdf_text(discharge_pdf)
        text2 = read_pdf_text(claim_pdf)
        full_text = text1 + "\n" + text2

        name = _extract_field(NAME_PATTERNS, full_text)
        disease = _extract_field(DISEASE_PATTERNS, full_text)
        total_amount = _extract_field(AMOUNT_PATTERNS, full_text)
        if total_amount == "Unknown":
            fallback = re.search(r"[₹$]?\s?\d[\d,]+(?:\.\d{1,2})?", full_text)
            if fallback:
                total_amount = fallback.group(0).strip()

        extracted = {
            "name": name,
            "disease": disease,
            "total_amount": total_amount,
        }

        print(f"[extract_claim] Extracted: {extracted}")
        return {"extracted": extracted}
