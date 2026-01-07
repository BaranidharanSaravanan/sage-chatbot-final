# src/generation/generator.py

from typing import List
import subprocess
import os
import shutil

from src.config import ALLOWED_MODELS
from src.utils.logger import get_logger

logger = get_logger(__name__)


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
"""

    def __init__(self, model_name: str = "llama3.1:8b", timeout: int = 60):
        logger.info(f"Initializing Generator | model={model_name}")

        if model_name not in ALLOWED_MODELS:
            logger.error(f"Blocked model requested: {model_name}")
            raise ValueError(
                f"Model '{model_name}' is not allowed. "
                f"Allowed models: {ALLOWED_MODELS}"
            )

        self.model_name = model_name
        self.timeout = timeout

        self.ollama_path = os.environ.get("OLLAMA_PATH") or shutil.which("ollama")
        if not self.ollama_path:
            logger.critical("Ollama executable not found")
            raise FileNotFoundError(
                "Ollama executable not found. "
                "Install Ollama or set OLLAMA_PATH."
            )

        logger.info("Generator initialized successfully")

    def generate(self, query: str, context: List[str]) -> str:
        if not context or all(not c.strip() for c in context):
            logger.warning("Empty context — refusing to generate")
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
            logger.info("Invoking Ollama")

            result = subprocess.run(
                [self.ollama_path, "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout
            )

            if result.returncode != 0 and not result.stdout.strip():
                logger.error("Ollama returned non-zero exit code")
                return "The language model encountered an internal error."

            output = result.stdout.strip()

            if not output:
                logger.warning("Empty response from model")
                return "I couldn't generate a response. Please try again."

            forbidden_phrases = [
                "as an ai",
                "i believe",
                "based on my knowledge",
                "generally",
                "typically",
                "usually"
            ]

            if any(p in output.lower() for p in forbidden_phrases):
                logger.warning("Hallucination pattern detected — response blocked")
                return (
                    "I don't have that information in my knowledge base. "
                    "Please contact the university administration or check the official website."
                )

            logger.info("Response generated successfully")
            return output

        except subprocess.TimeoutExpired:
            logger.error("Ollama call timed out")
            return "Response generation timed out. Please try again."

        except Exception:
            logger.exception("Unexpected generation error")
            return "An unexpected error occurred while generating the response."


# ----------------- Local Test -----------------
if __name__ == "__main__":
    context = [
        "The university library is open from 8 AM to 8 PM on weekdays.",
        "On weekends, the library is open from 9 AM to 5 PM."
    ]

    gen = Generator(model_name="llama3.1:8b")
    print(gen.generate("What are the library working hours?", context))
# src/generation/generator.py

from typing import List
import subprocess
import os
import shutil

from src.config import ALLOWED_MODELS
from src.utils.logger import get_logger

logger = get_logger(__name__)


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
"""

    def __init__(self, model_name: str = "llama3.1:8b", timeout: int = 60):
        logger.info(f"Initializing Generator | model={model_name}")

        if model_name not in ALLOWED_MODELS:
            logger.error(f"Blocked model requested: {model_name}")
            raise ValueError(
                f"Model '{model_name}' is not allowed. "
                f"Allowed models: {ALLOWED_MODELS}"
            )

        self.model_name = model_name
        self.timeout = timeout

        self.ollama_path = os.environ.get("OLLAMA_PATH") or shutil.which("ollama")
        if not self.ollama_path:
            logger.critical("Ollama executable not found")
            raise FileNotFoundError(
                "Ollama executable not found. "
                "Install Ollama or set OLLAMA_PATH."
            )

        logger.info("Generator initialized successfully")

    def generate(self, query: str, context: List[str]) -> str:
        if not context or all(not c.strip() for c in context):
            logger.warning("Empty context — refusing to generate")
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
            logger.info("Invoking Ollama")

            result = subprocess.run(
                [self.ollama_path, "run", self.model_name],
                input=prompt,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.timeout
            )

            if result.returncode != 0 and not result.stdout.strip():
                logger.error("Ollama returned non-zero exit code")
                return "The language model encountered an internal error."

            output = result.stdout.strip()

            if not output:
                logger.warning("Empty response from model")
                return "I couldn't generate a response. Please try again."

            forbidden_phrases = [
                "as an ai",
                "i believe",
                "based on my knowledge",
                "generally",
                "typically",
                "usually"
            ]

            if any(p in output.lower() for p in forbidden_phrases):
                logger.warning("Hallucination pattern detected — response blocked")
                return (
                    "I don't have that information in my knowledge base. "
                    "Please contact the university administration or check the official website."
                )

            logger.info("Response generated successfully")
            return output

        except subprocess.TimeoutExpired:
            logger.error("Ollama call timed out")
            return "Response generation timed out. Please try again."

        except Exception:
            logger.exception("Unexpected generation error")
            return "An unexpected error occurred while generating the response."


# ----------------- Local Test -----------------
if __name__ == "__main__":
    context = [
        "The university library is open from 8 AM to 8 PM on weekdays.",
        "On weekends, the library is open from 9 AM to 5 PM."
    ]

    gen = Generator(model_name="llama3.1:8b")
    print(gen.generate("What are the library working hours?", context))
