import uuid
from contextvars import ContextVar


request_id_context = ContextVar(
    "request_id",
    default=None
)


def create_request_id():
    request_id = str(uuid.uuid4())

    request_id_context.set(request_id)

    return request_id


def get_request_id():
    return request_id_context.get()