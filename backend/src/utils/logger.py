"""Structured logging configuration."""

import logging
import sys
from pathlib import Path

# Create logs directory
Path("logs").mkdir(exist_ok=True)

# Configure logging format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create formatter
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File handler for errors
file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler],
)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
