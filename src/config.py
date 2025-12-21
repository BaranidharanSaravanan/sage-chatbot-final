# src/utils/config.py

"""
Central configuration for SAGE Chatbot models.
Only approved, quantized models are listed here.
"""

AVAILABLE_MODELS = {
    "llama": {
        "name": "llama3.1:8b",
        "description": "LLaMA 3.1 8B Quantized (default, fastest)"
    },
    "deepseek": {
        "name": "deepseek-r1:8b",
        "description": "DeepSeek R1 8B Quantized (reasoning, general-purpose)"
    }
}

# Hard safety allowlist (used by Generator)
ALLOWED_MODELS = [
    "llama3.1:8b",
    "deepseek-r1:8b"
]

# Key from AVAILABLE_MODELS
DEFAULT_MODEL = "llama"
