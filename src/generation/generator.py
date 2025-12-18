# src/generation/generator.py

from typing import List
import subprocess
import json

class Generator:
    """
    Generator class for SAGE Chatbot.
    Uses LLaMA 3.1:8B quantized model via Ollama CLI.
    """

    def __init__(self, model_name: str = "llama3.1:8b", max_tokens: int = 512):
        """
        Args:
            model_name (str): Ollama model name
            max_tokens (int): Maximum tokens for response (currently unused)
        """
        self.model_name = model_name
        self.max_tokens = max_tokens

    def generate(self, query: str, context: List[str]) -> str:
        """
        Generate a context-grounded answer for the user query.
        
        Args:
            query (str): User input question
            context (List[str]): List of relevant text chunks from Retriever

        Returns:
            str: Generated answer
        """
        if not context:
            return "No relevant information found in the knowledge base."

        # Combine context chunks into single string
        context_text = "\n".join(context)

        # Construct prompt
        prompt = (
            "You are SAGE, a helpful assistant for the university.\n"
            "Answer the question using ONLY the context below.\n"
            "If the answer is not in the context, politely say you cannot answer.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {query}\nAnswer:"
        )

        try:
            # Call Ollama CLI
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt.encode("utf-8"),
                capture_output=True,
                check=True
            )

            output_text = result.stdout.decode("utf-8").strip()
            return output_text

        except subprocess.CalledProcessError as e:
            return f"Error generating answer: {e.stderr.decode('utf-8')}"

# ---------- Local Test ----------
if __name__ == "__main__":
    # Sample test
    sample_query = "What are the library working hours?"
    sample_context = [
        "The university library is open from 8 AM to 8 PM on weekdays.",
        "On weekends, the library is open from 9 AM to 5 PM."
    ]

    generator = Generator()
    answer = generator.generate(sample_query, sample_context)
    print("Generated Answer:\n", answer)
