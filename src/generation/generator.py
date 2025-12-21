# src/generation/generator.py

from typing import List
import subprocess
import os
import shutil

# ✅ SINGLE SOURCE OF TRUTH
from src.utils.config import ALLOWED_MODELS


class Generator:
    """
    Generator class for SAGE Chatbot.
    Uses Ollama safely on Windows / Linux / servers.
    """

    SYSTEM_PROMPT = """You are SAGE, a knowledgeable assistant for university students and staff.

YOUR CORE RULES (NEVER VIOLATE):
1. Answer ONLY using information from the provided Context section
2. If the Context does not contain the answer, respond with:
   "I don't have that information in my knowledge base. Please contact the university administration or check the official website."
3. Do NOT make assumptions or infer missing details
4. Do NOT use external knowledge
5. If the question is ambiguous, ask for clarification

RESPONSE GUIDELINES:
- Be concise and factual
- Use only the provided context
- Maintain a professional tone

IMPORTANT OUTPUT RULE:
- Do NOT mention chunk numbers, labels, or the word "context"
- Present the answer as a natural response to the user

FORBIDDEN BEHAVIORS:
- No hallucination
- No guessing
- No fabricated details
"""

    def __init__(self, model_name: str = "llama3.1:8b", timeout: int = 60):
        # 🔐 HARD SAFETY GATE (NOW CENTRALIZED)
        if model_name not in ALLOWED_MODELS:
            raise ValueError(
                f"Model '{model_name}' is not allowed. "
                f"Allowed models: {ALLOWED_MODELS}"
            )

        self.model_name = model_name
        self.timeout = timeout

        # Portable Ollama resolution (works in venv + server)
        self.ollama_path = os.environ.get("OLLAMA_PATH") or shutil.which("ollama")
        if not self.ollama_path:
            raise FileNotFoundError(
                "Ollama executable not found. "
                "Install Ollama or set OLLAMA_PATH environment variable."
            )

    def generate(self, query: str, context: List[str]) -> str:
        # --- Safety 1: empty context ---
        if not context or all(not c.strip() for c in context):
            return (
                "I don't have that information in my knowledge base. "
                "Please contact the university administration or check the official website."
            )

        context_text = "\n\n".join(context)

        prompt = f"""{self.SYSTEM_PROMPT}

===== CONTEXT =====
{context_text}

===== USER QUESTION =====
{query}

===== YOUR ANSWER =====
"""

        try:
            result = subprocess.run(
                [self.ollama_path, "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout
            )

            # --- Real failure only ---
            if result.returncode != 0 and not result.stdout.strip():
                return "The language model encountered an internal error. Please try again."

            output = result.stdout.strip()

            if not output:
                return "I couldn't generate a response. Please try rephrasing your question."

            # --- Anti-hallucination ---
            forbidden_phrases = [
                "as an ai",
                "i believe",
                "based on my knowledge",
                "generally",
                "in many universities",
                "typically",
                "usually"
            ]

            lowered_output = output.lower()
            if any(p in lowered_output for p in forbidden_phrases):
                return (
                    "I don't have that information in my knowledge base. "
                    "Please contact the university administration or check the official website."
                )

            return output

        except subprocess.TimeoutExpired:
            return "Response generation timed out. Please try a simpler question."

        except Exception:
            return "An unexpected error occurred while generating the response."


# ----------------- Local Test -----------------
if __name__ == "__main__":
    context = [
        "The university library is open from 8 AM to 8 PM on weekdays."
        "On weekends, the library is open from 9 AM to 5 PM."
    ]

    gen = Generator(model_name="deepseek-r1:8b")
    print(gen.generate("What are the library working hours?", context))
