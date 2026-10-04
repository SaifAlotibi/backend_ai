from fastapi import FastAPI

from routers import auth
from routers import conversations
from routers import chat

from exceptions import global_exception_handler


app = FastAPI(
    title="AI Agent Backend",
    version="1.0.0"
)


app.add_exception_handler(
    Exception,
    global_exception_handler
)


app.include_router(auth.router)
app.include_router(conversations.router)
app.include_router(chat.router)