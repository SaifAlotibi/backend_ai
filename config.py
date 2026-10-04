import os

from dotenv import load_dotenv

load_dotenv()

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000"
)

DATABASE_URL = os.getenv("DATABASE_URL")

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "dev-secret-change-this"
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