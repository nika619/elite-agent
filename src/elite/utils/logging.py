"""
elite.utils.logging
Structured logging configuration.
Supports both human-readable text format and JSON format.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone


class EliteTextFormatter(logging.Formatter):
    """
    Clean, colored text formatter for terminal output.
    Format: HH:MM:SS │ LEVEL │ logger │ message
    """

    LEVEL_COLORS = {
        "DEBUG": "\033[90m",     # gray
        "INFO": "\033[36m",      # cyan
        "WARNING": "\033[33m",   # yellow
        "ERROR": "\033[31m",     # red
        "CRITICAL": "\033[41m",  # red bg
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        color = self.LEVEL_COLORS.get(record.levelname, "")
        reset = self.RESET
        level = record.levelname.ljust(8)
        name = record.name.replace("elite.", "").ljust(20)
        msg = record.getMessage()

        formatted = f"{color}{ts} │ {level} │ {name} │ {msg}{reset}"

        if record.exc_info and record.exc_info[1]:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


class EliteJsonFormatter(logging.Formatter):
    """JSON formatter for structured log ingestion (e.g., CloudWatch, ELK)."""

    def format(self, record: logging.LogRecord) -> str:
        import json

        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extras if present
        for key in ("model", "base_url", "prompt_len", "response_len",
                     "agent", "confidence", "keywords", "command_preview"):
            if hasattr(record, key):
                log_entry[key] = getattr(record, key)

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(level: str = "INFO", format_type: str = "text") -> None:
    """
    Configure the root logger for the ELITE application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: 'text' for human-readable, 'json' for structured
    """
    root_logger = logging.getLogger("elite")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stderr)

    if format_type.lower() == "json":
        handler.setFormatter(EliteJsonFormatter())
    else:
        handler.setFormatter(EliteTextFormatter())

    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
