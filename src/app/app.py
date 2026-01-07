# src/app/app.py

import sys
from colorama import init, Fore, Style

from src.pipeline.rag_graph import run_rag
from src.config import AVAILABLE_MODELS, DEFAULT_MODEL
from src.utils.logger import logger

# Initialize colorama
init(autoreset=True)


def choose_model() -> str:
    """Let the user select a model, returning the Ollama-approved model name."""
    logger.info("Displaying available models to user")

    print(Fore.CYAN + Style.BRIGHT + "\nAvailable Models:")

    model_names = [AVAILABLE_MODELS[key]["name"] for key in AVAILABLE_MODELS]
    for i, name in enumerate(model_names, start=1):
        print(Fore.YELLOW + f"{i}. {name}")

    choice = input(
        Fore.GREEN
        + f"\nSelect model (1-{len(model_names)}) "
        + f"[default: {AVAILABLE_MODELS[DEFAULT_MODEL]['name']}]: "
        + Style.RESET_ALL
    ).strip()

    if not choice:
        default_model = AVAILABLE_MODELS[DEFAULT_MODEL]["name"]
        logger.info(f"No model selected, using default: {default_model}")
        return default_model

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(model_names):
            selected = model_names[idx]
            logger.info(f"User selected model: {selected}")
            return selected

    logger.warning("Invalid model selection, falling back to default")
    return AVAILABLE_MODELS[DEFAULT_MODEL]["name"]


def main():
    logger.info("SAGE chatbot started")

    print(Fore.CYAN + Style.BRIGHT + "\n=== Welcome to SAGE Chatbot ===")
    print(Fore.YELLOW + "Type 'exit' or 'quit' to leave the chatbot.\n")

    model_name = choose_model()
    logger.info(f"Using model: {model_name}")

    print(Fore.CYAN + f"\nUsing model: {model_name}\n")

    history = []

    try:
        while True:
            question = input(Fore.GREEN + "You: " + Style.RESET_ALL).strip()

            if question.lower() in ["exit", "quit"]:
                logger.info("User exited chatbot")
                print(Fore.CYAN + "Exiting SAGE. Goodbye!\n")
                break

            if not question:
                logger.warning("Empty question received")
                print(Fore.RED + "Please type a question.\n")
                continue

            logger.info(f"User question received: {question}")

            answer = run_rag(question, model_name=model_name)
            print(Fore.MAGENTA + "SAGE: " + Style.RESET_ALL + f"{answer}\n")

            history.append((question, answer))

    except KeyboardInterrupt:
        logger.info("Chatbot interrupted by user (Ctrl+C)")
        print(Fore.CYAN + "\n\nExiting SAGE. Goodbye!\n")
        sys.exit(0)

    logger.info("Chatbot session ended")
    print(Fore.YELLOW + "=== Session Summary ===")
    for i, (q, a) in enumerate(history, start=1):
        print(Fore.GREEN + f"{i}. You: {q}")
        print(Fore.MAGENTA + f"   SAGE: {a}\n")


if __name__ == "__main__":
    main()
