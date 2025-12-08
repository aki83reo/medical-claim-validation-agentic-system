# app/flow/claim_flow.py
from langgraph.graph import StateGraph, START, END
from app.agents.member_agent import MemberAgent
from app.agents.document_agent import DocumentAgent
from app.agents.claim_extraction_agent import ClaimExtractionAgent
from app.agents.policy_validation_agent import PolicyValidationAgent

class ClaimFlow:
    def __init__(self, rag_dir, collection_name, groq_model):
        self.member = MemberAgent()
        self.docs = DocumentAgent()
        self.extractor = ClaimExtractionAgent()
        self.policy = PolicyValidationAgent(
            rag_dir=rag_dir,
            model_name=groq_model,
            collection_name=collection_name
        )

        self.graph = StateGraph(dict)

        self.graph.add_node("ask_member_id", self.member.ask_member_id)
        self.graph.add_node("validate_member_id", self.member.validate_member_id)
        self.graph.add_node("request_docs", self.docs.request_docs)
        self.graph.add_node("extract_claim", self.extractor.extract_claim)
        self.graph.add_node("policy_validation", self.policy.policy_validation)

        self.graph.add_edge(START, "ask_member_id")
        self.graph.add_edge("ask_member_id", "validate_member_id")

        self.graph.add_conditional_edges(
            "validate_member_id",
            lambda s: bool(s.get("valid")),
            { True: "request_docs", False: "ask_member_id" }
        )

        self.graph.add_conditional_edges(
            "request_docs",
            lambda s: bool(s.get("docs_valid")),
            { True: "extract_claim", False: "request_docs" }
        )

        self.graph.add_edge("extract_claim", "policy_validation")
        self.graph.add_edge("policy_validation", END)

        self.flow = self.graph.compile()

    def run(self, initial=None):
        return self.flow.invoke(initial or {})
