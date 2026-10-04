import os


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "qwen3:1.7b"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/ai_agent.db"
)

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "dev-secret-change-this"
)

JWT_ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60