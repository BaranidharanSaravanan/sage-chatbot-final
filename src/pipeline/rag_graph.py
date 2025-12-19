# src/pipeline/rag_graph.py

# --- TEMP sys.path fix for running as module/script ---
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# ------------------- actual imports -------------------
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

from src.retrieval.retriever import Retriever
from src.generation.generator import Generator
from src.config import AVAILABLE_MODELS, DEFAULT_MODEL  # default model key

# -------- Resolve default model name --------
default_model_name = AVAILABLE_MODELS[DEFAULT_MODEL]["name"]

# -------- State Definition --------
class RAGState(TypedDict):
    question: str
    context: List[str]
    answer: str

# -------- Nodes --------
retriever = Retriever(top_k=5)

def get_generator(model_name: str = default_model_name) -> Generator:
    """Return a generator instance with the specified model."""
    return Generator(model_name=model_name)

def retrieve_node(state: RAGState) -> RAGState:
    docs = retriever.retrieve(state["question"])
    return {
        **state,
        "context": docs
    }

def generate_node(state: RAGState, model_name: str = default_model_name) -> RAGState:
    if not state["context"]:
        answer = "No relevant information found in the knowledge base."
    else:
        generator = get_generator(model_name)
        answer = generator.generate(state["question"], state["context"])

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

def run_rag(question: str, model_name: str = default_model_name) -> str:
    """
    Wrapper to run RAG graph for a single user question.
    model_name: pass the model to use (from config)
    Returns the answer string.
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

    # test default model
    result = run_rag(query)
    print("Question:", query)
    print("Answer:", result)

    # test explicit model
    result = run_rag(query, model_name="deepseek-coder:6.7b")
    print("Question:", query)
    print("Answer:", result)
