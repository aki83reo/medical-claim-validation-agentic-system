# main.py
from dotenv import load_dotenv
import os
print(os.getenv("GROQ_API_KEY"))
# Load env FIRST so GROQ_API_KEY is available to ChatGroq
load_dotenv()

from app.flow.claim_flow import ClaimFlow


if __name__ == "__main__":
    flow = ClaimFlow(
        rag_dir="/Users/ashis/Documents/langraph_medical_validation/vectorstores/policies",
        collection_name="health_policy_docs",
        groq_model="qwen/qwen3-32b",
    )

    result = flow.run()
    print("\n=== FINAL RESULT ===")
    print(result.get("policy_validation_result"))
