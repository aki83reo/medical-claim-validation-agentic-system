# app/agents/claim_extraction_agent.py
from app.utils.pdf_utils import read_pdf_text

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

        # TODO: Replace this with your regex extraction logic
        extracted = {
            "name": "John Doe",
            "disease": "Acute Plasmodium Falciparum Malaria",
            "total_amount": "$4,500",
        }

        print(f"[extract_claim] Extracted: {extracted}")
        return {"extracted": extracted}
