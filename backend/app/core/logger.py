import logging
import sys
from contextvars import ContextVar
from typing import Optional

request_id_var: ContextVar[str] = ContextVar("request_id", default="no-request")

LOG_FORMAT = "%(asctime)s [%(levelname)-8s] [%(name)-10s] [%(request_id)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


_loggers: dict[str, logging.Logger] = {}
_logging_configured = False


def setup_logging(level: str = "INFO") -> None:
    global _logging_configured
    if _logging_configured:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    if name in _loggers:
        return _loggers[name]
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    _loggers[name] = logger
    return logger


def redact_image(base64_str: str) -> str:
    if not base64_str:
        return "<empty>"
    prefix_len = min(50, len(base64_str))
    prefix = base64_str[:prefix_len]
    return f"{prefix}... ({len(base64_str)} chars redacted)"


def redact_session_id(sid: Optional[str]) -> str:
    if not sid:
        return "<none>"
    if len(sid) <= 8:
        return f"{sid[:3]}***"
    return f"{sid[:6]}***"


def get_request_id() -> str:
    return request_id_var.get()


def set_request_id(rid: str) -> None:
    request_id_var.set(rid)