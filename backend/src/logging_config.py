"""Production-ready logging configuration."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

_DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_MAX_LOG_FILE_SIZE = 10 * 1024 * 1024
_LOG_BACKUP_COUNT = 5


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


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Path | None = None,
) -> None:
    """Setup production logging.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type (json or text)
        log_file: Optional file path for logs
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.handlers.clear()

    console_handler = _create_stream_handler(log_format)
    root_logger.addHandler(console_handler)

    if log_file:
        file_handler = _create_file_handler(log_file, log_format)
        root_logger.addHandler(file_handler)


def _create_stream_handler(log_format: str) -> logging.StreamHandler:
    """Create console stream handler.

    Args:
        log_format: Format type (json or text)

    Returns:
        Configured StreamHandler
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_get_formatter(log_format))
    return handler


def _create_file_handler(log_file: Path, log_format: str) -> logging.Handler:
    """Create rotating file handler.

    Args:
        log_file: Path to log file
        log_format: Format type (json or text)

    Returns:
        Configured RotatingFileHandler
    """
    from logging.handlers import RotatingFileHandler

    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        log_file,
        maxBytes=_MAX_LOG_FILE_SIZE,
        backupCount=_LOG_BACKUP_COUNT,
    )
    handler.setFormatter(_get_formatter(log_format))
    return handler


def _get_formatter(log_format: str) -> logging.Formatter:
    """Get formatter based on format type.

    Args:
        log_format: Format type (json or text)

    Returns:
        Appropriate formatter instance
    """
    if log_format == "json":
        return JSONFormatter()
    return logging.Formatter(_DEFAULT_LOG_FORMAT)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
