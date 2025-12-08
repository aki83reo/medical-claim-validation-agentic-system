Medical Claim Validation – RAG + LangGraph + Groq

A production-ready prototype that validates medical insurance claims using a multi-agent pipeline built with:

LangGraph – stateful agent flow

Groq LLM (Qwen2.5 / Qwen3) – ultra-fast reasoning

FAISS Vector DB – policy document retrieval

Custom Agents for extraction + validation

🚀 Features
✔ 1. Claim Extraction Agent

Extracts from PDFs:

Name

Disease

Total claim amount

Uses PyPDFLoader + structured parsing.

✔ 2. RAG-based Policy Validation Agent

Validates claims using:

Retrieved policy clauses

Disease

Age

Claimed amount

Output includes:

{
  "coverage_status": "Fully covered | Partially covered | Not covered",
  "is_covered": true,
  "reason": "",
  "allowed_amount_estimate": null,
  "disallowed_reasons": [],
  "flags": []
}

✔ 3. LangGraph Orchestration

Flow:

member_id_check → document_load → claim_extraction → policy_validation → final output

✔ 4. Modular Production Code Structure
app/
 ├─ agents/
 │   ├─ claim_extractor.py
 │   ├─ policy_validation_agent.py
 │
 ├─ utils/
 │   ├─ rag_utils.py
 │
 ├─ flow/
 │   ├─ claim_flow.py
 │
 ├─ config/
 │   ├─ settings.py
 │
 └─ main.py

📦 Installation
1. Clone the repository
git clone <your_repo_url>
cd <repo_folder>

2. Create virtual environment
python3.11 -m venv new_env
source new_env/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Set API key

Create .env:

GROQ_API_KEY=your_key_here

🧠 Preprocess Policy PDFs (one-time)
python preprocess_policies_faiss.py


This creates FAISS index under vectorstores/.

▶️ Run the Claim Validation Pipeline
python main.py

🛠 Tech Stack

Python 3.11

LangChain / LangGraph

Groq LLM

FAISS

PyPDFLoader

📌 Notes

This repo does not include PDFs or vector DB (ignored for security).

Fully compatible with Mac M1/M2.

✅ 3. Push this project to GitHub safely

Follow these steps exactly:

STEP 1 — Initialize repo

Inside project folder:

git init

STEP 2 — Add files
git add .


❗ .gitignore will automatically exclude PDFs, vectorstores, env, etc.

STEP 3 — Commit
git commit -m "Initial production-ready medical claim validator"

STEP 4 — Create GitHub repository

Go to GitHub → New Repo → do NOT add README or .gitignore there

STEP 5 — Link local repo to GitHub
git remote add origin https://github.com/<username>/<repo-name>.git

STEP 6 — Push
git branch -M main
git push -u origin main