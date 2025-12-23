"""Centralized logging configuration for all modules."""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        for field in ("user_id", "request_id", "duration_ms", "environment", "chroma_mode"):
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        return json.dumps(log_data)


def setup_logging(level: str = "INFO", format_type: str = "json") -> None:
    """Setup centralized logging for entire project.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Format type (json or text)
    """
    log_level = os.getenv("LOG_LEVEL", level).upper()

    formatter: logging.Formatter
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
