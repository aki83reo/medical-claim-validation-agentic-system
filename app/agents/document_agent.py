# app/agents/document_agent.py
import os

class DocumentAgent:
    """Handles collecting 2 PDF paths."""

    def request_docs(self, state: dict) -> dict:
        """CLI version: ask user to input PDF paths."""

        def is_pdf(path: str) -> bool:
            ext = os.path.splitext(path)[1].lower()
            ok = ext == ".pdf"
            print(f"[is_pdf] '{path}' -> {ok}")
            return ok

        while True:
            claim_path = input("Enter CLAIM PDF path: ").strip()
            discharge_path = input("Enter DISCHARGE SUMMARY PDF path: ").strip()

            if not (is_pdf(claim_path) and is_pdf(discharge_path)):
                print("❌ Both files must be PDF. Try again.\n")
                continue

            return {
                "docs": [claim_path, discharge_path],
                "docs_valid": True,
            }
