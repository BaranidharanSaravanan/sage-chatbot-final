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
        "name": "deepseek-coder:6.7b",
        "description": "DeepSeek Coder 6.7B Quantized (fallback)"
    }
}

# Hard safety allowlist (used by Generator)
ALLOWED_MODELS = [
    "llama3.1:8b",
    "deepseek-coder:6.7b"
]

# Key from AVAILABLE_MODELS
DEFAULT_MODEL = "llama"
