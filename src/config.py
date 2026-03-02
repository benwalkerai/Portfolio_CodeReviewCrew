import os
from dotenv import load_dotenv

load_dotenv()

def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Missing required environment vairable: {key}")
    return value

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai") # "openai" or "ollama"

if LLM_PROVIDER == "openai":
    OPENAI_API_KEY = _require_env("OPENAI_API_KEY")
elif LLM_PROVIDER == "ollama":
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama3.2")
else:
    raise ValueError(f"Unsupport LLM_PROVIDER: {LLM_PROVIDER}. Use 'openai' or 'ollama'.")
VERBOSE = os.getenv("VERBOSE", "true").lower() == "true"

def get_llm():
    from crewai import LLM

    if LLM_PROVIDER == "openai":
        return LLM(
            model=f"openai/{MODEL_NAME}",
            api_key=OPENAI_API_KEY,
            verbose=VERBOSE,
        )
    else:
        return LLM(
            model=f"ollama/{MODEL_NAME}",
            base_url=OLLAMA_BASE_URL,
            verbose=VERBOSE,
        )