"""Production-ready logging configuration."""

import json
import logging
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging.

    Attributes:
        Custom fields: user_id, request_id, duration_ms
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        self._add_custom_fields(record, log_data)

        return json.dumps(log_data)

    @staticmethod
    def _add_custom_fields(
        record: logging.LogRecord, log_data: dict[str, Any]
    ) -> None:
        """Add custom fields to log data.

        Args:
            record: Log record
            log_data: Dictionary to update with custom fields
        """
        custom_fields = ["user_id", "request_id", "duration_ms"]
        for field in custom_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)


UVICORN_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": JSONFormatter,
        },
    },
    "handlers": {
        "default": {
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "json",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
