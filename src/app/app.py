# src/app/app.py

import sys
from colorama import init, Fore, Style

from src.pipeline.rag_graph import run_rag
from src.config import AVAILABLE_MODELS, DEFAULT_MODEL

# Initialize colorama
init(autoreset=True)


def choose_model() -> str:
    print(Fore.CYAN + Style.BRIGHT + "\nAvailable Models:")
    for i, model in enumerate(AVAILABLE_MODELS, start=1):
        print(Fore.YELLOW + f"{i}. {model}")

    choice = input(
        Fore.GREEN
        + f"\nSelect model (1-{len(AVAILABLE_MODELS)}) "
        + f"[default: {DEFAULT_MODEL}]: "
        + Style.RESET_ALL
    ).strip()

    if not choice:
        return DEFAULT_MODEL

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(AVAILABLE_MODELS):
            return AVAILABLE_MODELS[idx]

    print(Fore.RED + "Invalid choice. Using default model.\n")
    return DEFAULT_MODEL


def main():
    print(Fore.CYAN + Style.BRIGHT + "\n=== Welcome to SAGE Chatbot ===")
    print(Fore.YELLOW + "Type 'exit' or 'quit' to leave the chatbot.\n")

    # 🔹 Model selection (Step 3 requirement)
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
