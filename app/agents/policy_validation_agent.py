# app/agents/policy_validation_agent.py
import json
import re
from typing import Any, Dict

from langchain_groq import ChatGroq
from app.utils.rag_utils import PolicyRAG


def _parse_llm_json(raw: str) -> Dict[str, Any]:
    """
    Robustly parse JSON from an LLM response that may contain:
    - <think> ... </think>
    - plain text + JSON
    - ```json ... ``` blocks
    - multiple {...} segments

    Returns:
      - parsed dict on success
      - {"raw": raw} on failure
    """
    raw = (raw or "").strip()
    if not raw:
        return {"raw": raw}

    # 1) Try direct JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 2) Try ```json ... ``` blocks
    if "```" in raw:
        blocks = re.findall(r"```(?:json)?\s*(.*?)```", raw, re.DOTALL)
        for block in reversed(blocks):  # try last block first
            block = block.strip()
            if not block:
                continue
            try:
                return json.loads(block)
            except Exception:
                continue

    # 3) Try last {...} segment
    brace_segments = re.findall(r"\{[\s\S]*\}", raw)
    for segment in reversed(brace_segments):  # try last one first
        segment = segment.strip()
        if not segment:
            continue
        try:
            return json.loads(segment)
        except Exception:
            continue

    # 4) Give up – return raw text
    return {"raw": raw}


class PolicyValidationAgent:
    """
    RAG-based policy validator.
    """

    def __init__(self, rag_dir: str, model_name: str, collection_name: str):
        self.llm = ChatGroq(model=model_name)
        self.rag = PolicyRAG(
            persist_dir=rag_dir,
            collection_name=collection_name,
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )

    def policy_validation(self, state: dict) -> dict:
        extracted = state.get("extracted", {})
        disease = extracted.get("disease", "Unknown")
        claim_amount = extracted.get("total_amount", "Unknown")

        age = state.get("age")
        if age is None:
            try:
                age = int(input("Enter patient's age: "))
            except Exception:
                age = None

        print(
            f"[policy_validation] age={age}, "
            f"disease={disease}, claim_amount={claim_amount}"
        )

        # ---- RAG Retrieval ----
        query = (
            f"Disease: {disease}. Age: {age}. Claim amount: {claim_amount}. "
            "Find clauses related to coverage, waiting periods, co-pay, exclusions."
        )

        docs = self.rag.retrieve(query)
        print(f"[policy_validation] Retrieved {len(docs)} docs")

        if not docs:
            context = "No policy clauses retrieved. Answer conservatively."
        else:
            chunks = []
            for i, d in enumerate(docs, 1):
                chunks.append(f"[Clause {i}] {d.page_content}")
            context = "\n\n".join(chunks)

        # ---- Prompt ----
        instructions = """
Return ONLY a JSON with:
- coverage_status: "Fully covered" | "Partially covered" | "Not covered"
- is_covered: true/false
- reason: string
- allowed_amount_estimate: number or null
- disallowed_reasons: []
- flags: []
"""

        prompt = f"""
You are a medical claim underwriter.

Policy Context:
\"\"\"
{context}
\"\"\"

Claim details:
- Age: {age}
- Disease: {disease}
- Claimed Amount: {claim_amount}

{instructions}
"""

        resp = self.llm.invoke(prompt)
        raw = getattr(resp, "content", str(resp))

        print("\n[policy_validation] Raw LLM response:")
        print(raw)

        # ---- Robust JSON Parse ----
        data = _parse_llm_json(raw)

        print("[policy_validation] Final decision:", data)
        return {
            "policy_validation_result": data,
            "age": age,
        }
