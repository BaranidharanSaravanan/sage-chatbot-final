# src/generation/generator.py

from typing import List
import subprocess
import json

class Generator:
    """
    Generator class for SAGE Chatbot.
    Uses quantized LLM models via Ollama CLI with strict hallucination controls.
    """

    # System prompt with hallucination prevention
    SYSTEM_PROMPT = """You are SAGE, a knowledgeable assistant for university students and staff.

YOUR CORE RULES (NEVER VIOLATE):
1. Answer ONLY using information from the provided Context section
2. If the Context does not contain the answer, respond with: "I don't have that information in my knowledge base. Please contact the university administration or check the official website."
3. Do NOT make assumptions, infer, or generate information beyond what's explicitly stated
4. Do NOT combine information from different contexts unless directly asked
5. If the question is ambiguous, ask for clarification instead of guessing

RESPONSE GUIDELINES:
- Be concise and direct
- Cite specific details when available (e.g., timings, locations, procedures)
- If Context is partial, say "Based on available information..." and note what's missing
- Maintain a helpful, professional tone
- For procedural questions, list steps clearly

FORBIDDEN BEHAVIORS:
- Never fabricate details (phone numbers, dates, names, procedures)
- Never answer questions about topics not in the Context
- Never use external knowledge or training data
- Never say "I think" or "probably" - only state facts from Context"""

    def __init__(self, model_name: str = "llama3.1:8b", max_tokens: int = 512):
        """
        Args:
            model_name (str): Ollama model name (e.g., "llama3.1:8b", "deepseek-coder:6.7b")
            max_tokens (int): Maximum tokens for response
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
            str: Generated answer (grounded in context or refusal message)
        """
        # Handle empty context immediately
        if not context or all(not c.strip() for c in context):
            return "I don't have that information in my knowledge base. Please contact the university administration or check the official website."

        # Combine context chunks
        context_text = "\n\n".join([f"[Chunk {i+1}]\n{c}" for i, c in enumerate(context)])

        # Construct final prompt
        prompt = f"""{self.SYSTEM_PROMPT}

===== CONTEXT =====
{context_text}

===== USER QUESTION =====
{query}

===== YOUR ANSWER ====="""

        try:
            # Call Ollama CLI
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=prompt.encode("utf-8"),
                capture_output=True,
                check=True,
                timeout=30  # 30 second timeout
            )

            output_text = result.stdout.decode("utf-8").strip()
            
            # Safety check: if response is empty
            if not output_text:
                return "I encountered an error generating a response. Please try rephrasing your question."
            
            return output_text

        except subprocess.TimeoutExpired:
            return "Response generation timed out. Please try a simpler question."
        
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode("utf-8") if e.stderr else "Unknown error"
            return f"I encountered an error: {error_msg}. Please try again."
        
        except FileNotFoundError:
            return "Model not available. Please ensure Ollama is installed and the model is downloaded."
        
        except Exception as e:
            return f"Unexpected error: {str(e)}"


# ---------- Local Test ----------
if __name__ == "__main__":
    print("=== SAGE Generator Local Test ===\n")
    
    # Test 1: Normal query with context
    print("Test 1: Normal Query")
    sample_query = "What are the library working hours?"
    sample_context = [
        "The university library is open from 8 AM to 8 PM on weekdays.",
        "On weekends, the library is open from 9 AM to 5 PM."
    ]
    
    generator = Generator()
    answer = generator.generate(sample_query, sample_context)
    print(f"Q: {sample_query}")
    print(f"A: {answer}\n")
    
    # Test 2: Query with no context (should refuse)
    print("Test 2: Empty Context (Should Refuse)")
    answer = generator.generate("What's the weather today?", [])
    print(f"Q: What's the weather today?")
    print(f"A: {answer}\n")
    
    # Test 3: Out-of-scope query (should refuse)
    print("Test 3: Out-of-Scope Query")
    out_of_scope_context = ["The library has 50,000 books in the collection."]
    answer = generator.generate("What is the hostel curfew time?", out_of_scope_context)
    print(f"Q: What is the hostel curfew time?")
    print(f"A: {answer}\n")