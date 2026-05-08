import uuid
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import setup_logging, get_logger, set_request_id
from app.routes import router

setup_logging(settings.log_level)


class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("uvicorn")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex[:8]
        set_request_id(request_id)
        scope.setdefault("state", {})["request_id"] = request_id

        method = scope["method"]
        path = scope["path"]

        self.logger.info(f"{method} {path} START")

        status_code = 0
        start_time = time.monotonic()

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            self.logger.error(f"{method} {path} ERROR {type(e).__name__}: {e}")
            raise
        finally:
            elapsed_ms = (time.monotonic() - start_time) * 1000
            self.logger.info(f"{method} {path} END status={status_code} duration={elapsed_ms:.1f}ms")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered room Feng Shui evaluator.",
)

app.add_middleware(LoggingMiddleware)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)
