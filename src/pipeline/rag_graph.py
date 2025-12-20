# src/pipeline/rag_graph.py

# --- TEMP sys.path fix for direct execution ---
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ------------------- imports -------------------
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from src.retrieval.retriever import Retriever
from src.generation.generator import Generator
from src.config import AVAILABLE_MODELS, DEFAULT_MODEL


# -------- Resolve default model name --------
DEFAULT_MODEL_NAME = AVAILABLE_MODELS[DEFAULT_MODEL]["name"]


# -------- State Definition --------
class RAGState(TypedDict):
    question: str
    context: List[str]
    answer: str
    model_name: str


# -------- Core Components --------
retriever = Retriever(top_k=5)


def retrieve_node(state: RAGState) -> RAGState:
    """Retrieve relevant documents for the question."""
    docs = retriever.retrieve(state["question"])

    return {
        **state,
        "context": docs
    }


def generate_node(state: RAGState) -> RAGState:
    """Generate answer using retrieved context and selected model."""
    generator = Generator(model_name=state["model_name"])
    answer = generator.generate(state["question"], state["context"])

    return {
        **state,
        "answer": answer
    }


# -------- Graph Definition --------
graph = StateGraph(RAGState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

rag_app = graph.compile()


# -------- Public API --------
def run_rag(question: str, model_name: str = DEFAULT_MODEL_NAME) -> str:
    """
    Run the RAG pipeline for a single question.

    Args:
        question (str): User query
        model_name (str): Ollama model name

    Returns:
        str: Final answer
    """
    result = rag_app.invoke({
        "question": question,
        "context": [],
        "answer": "",
        "model_name": model_name
    })

    return result["answer"]


# -------- Local Test --------
if __name__ == "__main__":
    query = "What are the library working hours?"

    print("Default model test:")
    print(run_rag(query))
    print("-" * 50)

    print("Explicit model test:")
    print(run_rag(query, model_name="deepseek-coder:6.7b"))
