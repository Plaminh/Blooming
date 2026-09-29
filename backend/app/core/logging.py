import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone


_RESERVED = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime"}
request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)
_SENSITIVE_PARTS = ("token", "authorization", "password", "secret", "api_key", "email")


def _is_sensitive(key: str) -> bool:
    normalized = key.lower()
    return any(part in normalized for part in _SENSITIVE_PARTS)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = request_id_context.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and isinstance(value, (str, int, float, bool, type(None))):
                payload[key] = "[REDACTED]" if _is_sensitive(key) else value
        if record.exc_info:
            payload["exception"] = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestContextFilter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
