# src/pipeline/rag_graph.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List

from src.retrieval.retriever import Retriever


# -------- State Definition --------
class RAGState(TypedDict):
    question: str
    context: List[str]
    answer: str


# -------- Nodes --------
retriever = Retriever(top_k=5)


def retrieve_node(state: RAGState) -> RAGState:
    docs = retriever.retrieve(state["question"])
    return {
        **state,
        "context": docs
    }


def generate_node(state: RAGState) -> RAGState:
    if not state["context"]:
        answer = "No relevant information found in the knowledge base."
    else:
        answer = "ANSWER_GENERATION_PLACEHOLDER"

    return {
        **state,
        "answer": answer
    }


# -------- Graph --------
graph = StateGraph(RAGState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

rag_app = graph.compile()


# -------- Local Test --------
if __name__ == "__main__":
    query = "What are the library working hours?"

    result = rag_app.invoke({
        "question": query,
        "context": [],
        "answer": ""
    })

    print("Question:", query)
    print("Answer:", result["answer"])
