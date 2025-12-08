"""
preprocess_policies.py

One-time (or occasional) script to:
- Load policy PDFs from a folder
- Chunk text
- Add metadata (policy_id, insurer, plan_name, etc.)
- Store in a persistent FAISS vector store

Run:
    python preprocess_policies.py
"""

import os
from pathlib import Path
from typing import List, Dict

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS   # 🔁 CHANGED: Chroma → FAISS


# ========= CONFIG =========

# Folder where your policy PDFs live
POLICY_PDF_DIR = "/Users/ashis/Documents/langraph_medical_validation/policies"  # put your PDFs here

# Persistent directory for FAISS index (folder where FAISS files will be stored)
VECTOR_DB_DIR = "./vectorstores/policies_faiss"  # 🔁 new folder name for FAISS index

# Name of the collection (kept for semantics, not used by FAISS directly)
COLLECTION_NAME = "health_policy_docs"

# Chunking config
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


# ========= HELPERS =========

def infer_policy_metadata_from_filename(pdf_path: Path) -> Dict:
    """
    Simple metadata inference based on file name.

    Example filename:
        Policy_Standard_5Lakh_Individual.pdf

    We’ll derive:
        policy_id: "Policy_Standard_5Lakh_Individual"
        insurer: "SyntheticInsurer"
        plan_name: "Standard_5Lakh_Individual"
        version: "v1"

    Adjust this to your own naming convention later.
    """
    stem = pdf_path.stem  # filename without .pdf
    parts = stem.split("_")

    meta: Dict[str, str] = {
        "policy_id": stem,
        "insurer": "SyntheticInsurer",
        "plan_name": "_".join(parts[1:]) if len(parts) > 1 else stem,
        "version": "v1",
        "file_name": pdf_path.name,
        "source": str(pdf_path),
    }
    return meta


def load_policy_pdfs(pdf_dir: str) -> List[Document]:
    """
    Load all PDFs from the folder as LangChain Documents.
    Each page becomes a Document with metadata including basic policy info.
    """
    pdf_dir_path = Path(pdf_dir)
    if not pdf_dir_path.exists():
        raise FileNotFoundError(f"Policy PDF folder not found: {pdf_dir}")

    all_docs: List[Document] = []

    for pdf_path in pdf_dir_path.glob("*.pdf"):
        print(f"📄 Loading: {pdf_path.name}")
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()  # list[Document], one per page

        base_meta = infer_policy_metadata_from_filename(pdf_path)

        for page in pages:
            # merge base metadata with page metadata
            merged_meta = {**base_meta, **(page.metadata or {})}
            page.metadata = merged_meta
            all_docs.append(page)

    print(f"✅ Loaded {len(all_docs)} pages from {pdf_dir_path}")
    return all_docs


def chunk_documents(
    docs: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[Document]:
    """
    Split documents into overlapping chunks for better retrieval.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        # try to keep paragraphs & sentences intact where possible
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    print(f"✂️  Chunking {len(docs)} documents...")
    chunks = splitter.split_documents(docs)
    print(f"✅ Produced {len(chunks)} chunks.")
    return chunks


def build_or_update_vectorstore(
    chunks: List[Document],
    persist_directory: str = VECTOR_DB_DIR,
    collection_name: str = COLLECTION_NAME,  # kept for API symmetry, not used by FAISS
):
    """
    Create a FAISS vectorstore with the given chunks.

    This will overwrite the existing index in `persist_directory`.
    To rebuild from scratch, just run this script again.
    """
    os.makedirs(persist_directory, exist_ok=True)

    print("🧠 Initializing HuggingFace embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print(f"💾 Building FAISS index at: {persist_directory}")
    vectordb = FAISS.from_documents(chunks, embeddings)

    # Persist FAISS index to disk
    vectordb.save_local(persist_directory)

    print("✅ FAISS vector store built & saved.")
    return vectordb


# ========= MAIN =========

def main():
    print("🚀 Starting policy preprocessing...")

    # 1. Load raw PDFs as documents
    docs = load_policy_pdfs(POLICY_PDF_DIR)

    # 2. Chunk them
    chunks = chunk_documents(docs)

    # 3. Build / update vector DB
    _ = build_or_update_vectorstore(chunks)

    print("🎉 Done. Policy chunks are stored in the FAISS vector store.")


if __name__ == "__main__":
    main()
