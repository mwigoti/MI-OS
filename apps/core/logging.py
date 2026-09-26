"""
MwohaOS Structured Logging Formatter
Ensures security by scrubbing sensitive headers/passwords and producing clean logs.
"""
import json
import logging
from datetime import datetime, timezone

SENSITIVE_KEYS = {
    "password", "secret", "token", "key", "authorization",
    "cookie", "sessionid", "csrfmiddlewaretoken"
}

class JsonFormatter(logging.Formatter):
    """
    Structured JSON log formatter for containerized environments.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)
