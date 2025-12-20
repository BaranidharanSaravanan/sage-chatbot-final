from typing import List
import subprocess


class Generator:
    """
    Generator class for SAGE Chatbot.
    Works only with approved quantized Ollama models.
    """

    # Explicit allowlist (VERY important for team safety)
    ALLOWED_MODELS = [
        "llama3.1:8b",
        "deepseek-coder:6.7b"
    ]

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
        """
        Args:
            model_name (str): Approved Ollama model name
            timeout (int): Max seconds to wait for model response
        """

        if model_name not in self.ALLOWED_MODELS:
            raise ValueError(
                f"Model '{model_name}' is not allowed. "
                f"Allowed models: {self.ALLOWED_MODELS}"
            )

        self.model_name = model_name
        self.timeout = timeout

    def generate(self, query: str, context: List[str]) -> str:
        """
        Generate a grounded answer using retrieved context.
        """

        # ---------- SAFETY 1: Empty or useless context ----------
        if not context or all(not c.strip() for c in context):
            return (
                "I don't have that information in my knowledge base. "
                "Please contact the university administration or check the official website."
            )

        # ---------- SAFETY 2: Merge context (NO chunk labels) ----------
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
                ["ollama", "run", self.model_name],
                input=prompt.encode("utf-8"),
                capture_output=True,
                timeout=self.timeout
            )

            # ---------- SAFETY 3: Ollama stderr check ----------
            if result.stderr and result.stderr.strip():
                return (
                    "The language model encountered an internal error. "
                    "Please try again."
                )

            output = result.stdout.decode("utf-8").strip()

            # ---------- SAFETY 4: Empty or junk output ----------
            if not output:
                return (
                    "I couldn't generate a response. "
                    "Please try rephrasing your question."
                )

            # ---------- SAFETY 5: Anti-hallucination post-check ----------
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
            if any(phrase in lowered_output for phrase in forbidden_phrases):
                return (
                    "I don't have that information in my knowledge base. "
                    "Please contact the university administration or check the official website."
                )

            return output

        except subprocess.TimeoutExpired:
            return "Response generation timed out. Please try a simpler question."

        except FileNotFoundError:
            return "Ollama is not installed or not found in PATH."

        except Exception:
            return "An unexpected error occurred while generating the response."


# ---------- Local Test ----------
if __name__ == "__main__":
    print("=== Generator Stability Test ===\n")

    context = [
        "The university library is open from 8 AM to 8 PM on weekdays.",
        "On weekends, the library is open from 9 AM to 5 PM."
    ]

    gen = Generator(model_name="llama3.1:8b")
    answer = gen.generate("What are the library working hours?", context)
    print(answer)
