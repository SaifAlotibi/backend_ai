from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from logging_config import setup_logging
from routers import auth
from routers import conversations
from routers import chat

from exceptions import global_exception_handler

from metrics import metrics

from config import CORS_ORIGINS
from request_context import create_request_id
setup_logging()

app = FastAPI(
    title="AI Agent Backend",
    version="1.0.0"
)

logger = logging.getLogger(__name__)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):

    request_id = create_request_id()

    start_time = time.perf_counter()

    logger.info(
        "Request started | request_id=%s | method=%s | path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    response = await call_next(request)

    elapsed = time.perf_counter() - start_time

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed | request_id=%s | status=%s | latency=%.3fs",
        request_id,
        response.status_code,
        elapsed,
    )

    return response

app.add_middleware(
    CORSMiddleware, 
    allow_origins=[CORS_ORIGINS],
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_exception_handler(
    Exception,
    global_exception_handler
)


app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)

@app.get("/metrics")
def get_metrics():
    return metrics.get_metrics()