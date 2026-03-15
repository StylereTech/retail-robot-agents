"""Logging utility."""
import logging
from rich.logging import RichHandler

def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger(name)
