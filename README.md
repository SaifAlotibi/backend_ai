# AI Backend — FastAPI, Ollama, RAG, and Agent Tools

A containerized AI backend built with **FastAPI** and **Python**. It combines local LLM inference through Ollama, an agent that can call tools, PDF-based retrieval-augmented generation (RAG), persistent conversations, and observability features.

This repository is a backend-focused portfolio project. It does not include a frontend.

## Highlights

- **REST API and authentication** — JWT-protected endpoints for identity and conversation management.
- **Non-streaming and streaming chat** — regular responses through `POST /chat` and streamed responses through `POST /chat/stream`.
- **Tool-using agent** — an agent loop that can call a restricted arithmetic calculator and search the knowledge base.
- **PDF RAG** — PDF text extraction, chunking, embedding generation, FAISS-based retrieval, and a reranking component.
- **Conversation memory** — message persistence and conversation summaries to help manage longer conversations.
- **PostgreSQL persistence** — SQLModel-based database models and Alembic migrations.
- **Resilience and observability** — retries, circuit-breaker logic, request IDs, structured logging, rate limiting, OpenTelemetry instrumentation, Jaeger, and an application metrics endpoint.
- **Docker Compose** — runs the backend alongside PostgreSQL, Ollama, and Jaeger.

## Architecture

```text
Client
  │
  ▼
FastAPI ── authentication / conversation routes / chat routes / metrics
  │
  ▼
Chat service ── conversation history and summaries ── PostgreSQL
  │
  ▼
Agent loop ── Ollama chat model
  │             │
  │             ├── calculator tool
  │             └── knowledge-search tool
  │                         │
  │                         ▼
  │                  PDF RAG pipeline
  │                  extraction → chunks → embeddings → FAISS retrieval → reranking
  │
  └── logs, request IDs, OpenTelemetry traces ── Jaeger
```

## Technology stack

- Python, FastAPI, Uvicorn
- SQLModel, PostgreSQL, Alembic
- Ollama with `qwen3:1.7b` for chat and `nomic-embed-text` for embeddings
- PyPDF, Ollama embeddings, FAISS
- JWT authentication and Argon2 password hashing
- Docker Compose
- OpenTelemetry and Jaeger
- Pytest

## Requirements

- Docker Desktop or Docker Engine with Docker Compose
- Sufficient memory and disk space for the Ollama image and model weights
- A configured `.env` file (see below)

The recommended way to run this project is through Docker Compose. The hostname `postgres` and the Ollama URL shown below are intended for services communicating on the Compose network; they are not the right hostnames for a Python process running directly on Windows.


## Configuration

Create a `.env` file in the repository root. Docker Compose reads this file to configure the backend and its supporting services.

Use the following configuration for local development:

```env
# Ollama
OLLAMA_URL=http://ollama:11434
MODEL_NAME=qwen3:1.7b
EMBEDDING_MODEL=nomic-embed-text

# PostgreSQL
DATABASE_URL=postgresql+psycopg://ai_user:ai_password@postgres:5432/ai_database

# JWT Authentication
JWT_SECRET_KEY=REPLACE_WITH_YOUR_GENERATED_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
CORS_ORIGINS=http://localhost:3000
MAX_HISTORY_MESSAGES=20
RECENT_MESSAGES=10
```

### Generate a JWT Secret Key

Generate a secure secret key using Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Replace `REPLACE_WITH_YOUR_GENERATED_KEY` in your local `.env` file with the generated value.

**Security notes:**
- Never commit your actual `.env` file or JWT secret to GitHub.
- The PostgreSQL credentials above are development defaults, not production credentials.
- The Ollama URL uses `ollama:11434` because the backend connects to Ollama through Docker Compose's internal network.

## Run with Docker Compose

1. Configure `.env` using the settings above and the PostgreSQL credentials in `compose.yaml`.
2. Build and start the services:

   ```powershell
   docker compose up -d --build
   ```

3. Download the required models into the Ollama service (on a fresh setup):

   ```powershell
   docker compose exec ollama ollama pull qwen3:1.7b
   docker compose exec ollama ollama pull nomic-embed-text
   ```

4. Check service status:

   ```powershell
   docker compose ps
   ```

5. Open the interactive API documentation:

   - FastAPI Swagger UI: <http://localhost:8000/docs>
   - Jaeger UI: <http://localhost:16686>

The project includes two example PDF documents in `documents/`. Generated RAG index files are local artifacts under `rag_store/` and are excluded from Git; they may need to be generated or rebuilt according to the RAG pipeline's initialization behavior when setting up a fresh environment.

## API endpoints

The running OpenAPI schema exposes these endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/register` | Register a user |
| `POST` | `/auth/login` | Log in and obtain an access token |
| `GET` | `/auth/me` | Get the authenticated user's identity |
| `GET` | `/conversations` | List the authenticated user's conversations |
| `POST` | `/conversations` | Create a conversation |
| `GET` | `/conversations/{conversation_id}` | Retrieve a conversation |
| `POST` | `/chat` | Send a non-streaming chat request |
| `POST` | `/chat/stream` | Stream a chat response |
| `GET` | `/metrics` | Access application metrics |

Use Swagger UI at `/docs` to inspect the current request schemas and response formats. Authenticated routes require a valid access token.

## Tests

Run the automated test suite inside the Docker Compose network so the hostname `postgres` resolves correctly:

```powershell
docker compose run --rm backend python -m pytest -q
```

The suite was verified in the development environment with **7 tests passing**. A deprecation warning from the FastAPI/Starlette test-client stack may appear; it did not cause the tests to fail in that run.

A manual RAG smoke-test script is available at `tests/rag_demo.py`. It makes a real embedding/RAG request, so the services and embedding model must be available before running it.

## Repository notes

- `.env` is ignored by Git; keep credentials and signing keys local.
- `rag_store/` is ignored because the FAISS index and related files are generated artifacts.
- The two PDFs in `documents/` are example policy documents for demonstrating retrieval.
- This repository focuses on backend services and API behavior; it does not include a web UI.

## Current scope and limitations

This is a local-development and portfolio project, not a claim of production certification. Before deploying it for real users, review deployment-specific secret management, access controls, database backup and migration procedures, observability and alerting, model performance under load, and streaming cancellation behavior.
