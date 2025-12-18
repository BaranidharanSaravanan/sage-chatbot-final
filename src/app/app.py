# src/app/app.py

import sys
from src.pipeline.rag_graph import run_rag
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def main():
    print(Fore.CYAN + Style.BRIGHT + "\n=== Welcome to SAGE Chatbot ===")
    print(Fore.YELLOW + "Type 'exit' or 'quit' to leave the chatbot.\n")

    history = []

    try:
        while True:
            # Get user input
            question = input(Fore.GREEN + "You: " + Style.RESET_ALL).strip()
            if question.lower() in ["exit", "quit"]:
                print(Fore.CYAN + "Exiting SAGE. Goodbye!\n")
                break

            if not question:
                print(Fore.RED + "Please type a question.\n")
                continue

            # Call RAG pipeline
            answer = run_rag(question)
            print(Fore.MAGENTA + "SAGE: " + Style.RESET_ALL + f"{answer}\n")

            # Store history
            history.append((question, answer))

    except KeyboardInterrupt:
        print(Fore.CYAN + "\n\nExiting SAGE. Goodbye!\n")
        sys.exit(0)

    # Optional: print chat history on exit
    print(Fore.YELLOW + "=== Session Summary ===")
    for i, (q, a) in enumerate(history, start=1):
        print(Fore.GREEN + f"{i}. You: {q}")
        print(Fore.MAGENTA + f"   SAGE: {a}\n")


if __name__ == "__main__":
    main()
