# src/app/app.py

import sys
from colorama import init, Fore, Style

from src.pipeline.rag_graph import run_rag
from src.config import AVAILABLE_MODELS, DEFAULT_MODEL

# Initialize colorama
init(autoreset=True)


def choose_model() -> str:
    """Let the user select a model, returning the Ollama-approved model name."""
    print(Fore.CYAN + Style.BRIGHT + "\nAvailable Models:")

    # Map numeric options to Ollama model names
    model_names = [AVAILABLE_MODELS[key]["name"] for key in AVAILABLE_MODELS]
    for i, name in enumerate(model_names, start=1):
        print(Fore.YELLOW + f"{i}. {name}")

    choice = input(
        Fore.GREEN
        + f"\nSelect model (1-{len(model_names)}) "
        + f"[default: {AVAILABLE_MODELS[DEFAULT_MODEL]['name']}]: "
        + Style.RESET_ALL
    ).strip()

    # Default model
    if not choice:
        return AVAILABLE_MODELS[DEFAULT_MODEL]["name"]

    # Numeric choice
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(model_names):
            return model_names[idx]

    print(Fore.RED + "Invalid choice. Using default model.\n")
    return AVAILABLE_MODELS[DEFAULT_MODEL]["name"]


def main():
    print(Fore.CYAN + Style.BRIGHT + "\n=== Welcome to SAGE Chatbot ===")
    print(Fore.YELLOW + "Type 'exit' or 'quit' to leave the chatbot.\n")

    # 🔹 Model selection
    model_name = choose_model()
    print(Fore.CYAN + f"\nUsing model: {model_name}\n")

    history = []

    try:
        while True:
            question = input(Fore.GREEN + "You: " + Style.RESET_ALL).strip()

            if question.lower() in ["exit", "quit"]:
                print(Fore.CYAN + "Exiting SAGE. Goodbye!\n")
                break

            if not question:
                print(Fore.RED + "Please type a question.\n")
                continue

            # 🔹 Pass selected model into RAG
            answer = run_rag(question, model_name=model_name)
            print(Fore.MAGENTA + "SAGE: " + Style.RESET_ALL + f"{answer}\n")

            history.append((question, answer))

    except KeyboardInterrupt:
        print(Fore.CYAN + "\n\nExiting SAGE. Goodbye!\n")
        sys.exit(0)

    print(Fore.YELLOW + "=== Session Summary ===")
    for i, (q, a) in enumerate(history, start=1):
        print(Fore.GREEN + f"{i}. You: {q}")
        print(Fore.MAGENTA + f"   SAGE: {a}\n")


if __name__ == "__main__":
    main()
