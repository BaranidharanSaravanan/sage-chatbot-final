# src/pipeline/rag_graph.py

# --- TEMP sys.path fix for direct execution ---
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from typing import TypedDict, List
from langgraph.graph import StateGraph, END

from src.retrieval.retriever import Retriever
from src.generation.generator import Generator
from src.config import AVAILABLE_MODELS, DEFAULT_MODEL
from src.utils.logger import logger


DEFAULT_MODEL_NAME = AVAILABLE_MODELS[DEFAULT_MODEL]["name"]


class RAGState(TypedDict):
    question: str
    context: List[str]
    answer: str
    model_name: str


retriever = Retriever(top_k=5)


def resolve_model_name(model_key_or_name: str) -> str:
    for cfg in AVAILABLE_MODELS.values():
        if model_key_or_name == cfg["name"]:
            return model_key_or_name

    resolved = AVAILABLE_MODELS.get(
        model_key_or_name,
        AVAILABLE_MODELS[DEFAULT_MODEL]
    )["name"]

    logger.info(f"Resolved model '{model_key_or_name}' → '{resolved}'")
    return resolved


def retrieve_node(state: RAGState) -> RAGState:
    logger.info(f"Retrieval started for question: {state['question']}")

    docs = retriever.retrieve(state["question"])

    logger.info(f"Retrieved {len(docs)} context chunks")

    return {
        **state,
        "context": docs
    }


def generate_node(state: RAGState) -> RAGState:
    resolved_model = resolve_model_name(state["model_name"])
    logger.info(f"Generation started using model: {resolved_model}")

    generator = Generator(model_name=resolved_model)
    answer = generator.generate(state["question"], state["context"])

    logger.info("Generation completed")

    return {
        **state,
        "answer": answer
    }


graph = StateGraph(RAGState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

rag_app = graph.compile()


def run_rag(question: str, model_name: str = DEFAULT_MODEL_NAME) -> str:
    logger.info(f"RAG pipeline invoked | model={model_name}")

    result = rag_app.invoke({
        "question": question,
        "context": [],
        "answer": "",
        "model_name": model_name
    })

    logger.info("RAG pipeline completed")
    return result["answer"]


if __name__ == "__main__":
    query = "What are the library working hours?"

    print("Key-based model test:")
    print(run_rag(query, model_name="llama"))
    print("-" * 50)

    print("Full-name model test:")
    print(run_rag(query, model_name="deepseek-coder:6.7b"))
