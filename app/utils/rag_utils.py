# app/utils/rag_utils.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class PolicyRAG:
    """
    Loads an existing Chroma vector DB and provides a retriever.
    """

    def __init__(self, persist_dir: str, collection_name: str, model_name: str):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)

        self.db = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_dir,
        )

        self.retriever = self.db.as_retriever(
            search_kwargs={"k": 6}   # tunes later
        )

    def retrieve(self, query: str):
        """Return relevant policy chunks."""
        try:
            return self.retriever.invoke(query)
        except Exception as e:
            print(f"[PolicyRAG] Retrieval error: {e}")
            return []
