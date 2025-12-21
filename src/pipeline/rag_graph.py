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
    model_name: str   # always holds FULL ollama model name


# -------- Core Components --------
retriever = Retriever(top_k=5)


def resolve_model_name(model_key_or_name: str) -> str:
    """
    Accepts either:
    - model key (e.g., 'llama', 'deepseek')
    - full model name (e.g., 'llama3.1:8b')

    Returns:
    - full Ollama model name
    """
    # If already a full model name, return as-is
    for cfg in AVAILABLE_MODELS.values():
        if model_key_or_name == cfg["name"]:
            return model_key_or_name

    # Otherwise treat it as a key
    return AVAILABLE_MODELS.get(
        model_key_or_name,
        AVAILABLE_MODELS[DEFAULT_MODEL]
    )["name"]


def retrieve_node(state: RAGState) -> RAGState:
    """Retrieve relevant documents for the question."""
    docs = retriever.retrieve(state["question"])

    return {
        **state,
        "context": docs
    }


def generate_node(state: RAGState) -> RAGState:
    """Generate answer using retrieved context and selected model."""
    resolved_model = resolve_model_name(state["model_name"])

    generator = Generator(model_name=resolved_model)
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
        model_name (str): model key OR full Ollama model name

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

    print("Key-based model test:")
    print(run_rag(query, model_name="llama"))
    print("-" * 50)

    print("Full-name model test:")
    print(run_rag(query, model_name="deepseek-coder:6.7b"))
