#import uuid4

from contextvars import ContextVar
from starlette.types import ASGIApp, Receive, Scope, Send

REQUEST_ID_CTX_KEY = "request_id"
REQUEST_CTX_KEY = "request"

_request_id_ctx_var: ContextVar[str] = ContextVar(REQUEST_ID_CTX_KEY, default=None)
_request_ctx_var: ContextVar[str] = ContextVar(REQUEST_ID_CTX_KEY, default=None)

def get_request_id() -> str:
    return _request_id_ctx_var.get()

def get_request() -> str:
    return _request_ctx_var.get()

def set_request(request) -> None:
    _request_ctx_var.set(request)

class AuthenticationMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        #request_id = _request_id_ctx_var.set(str(uuid4()))
        request = _request_ctx_var.set(scope)

        await self.app(scope, receive, send)

        #_request_id_ctx_var.reset(request_id)
        _request_ctx_var.reset(request)