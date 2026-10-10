import os

from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "nomic-embed-text"
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY must be configured in the environment."
    )

if len(JWT_SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError(
        "JWT_SECRET_KEY must contain at least 32 bytes."
    )

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "30"
    )
)

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000"
)

MAX_HISTORY_MESSAGES = int(
    os.getenv(
        "MAX_HISTORY_MESSAGES",
        "20"
    )
)

RECENT_MESSAGES = int(
    os.getenv(
        "RECENT_MESSAGES",
        "10"
    )
)
