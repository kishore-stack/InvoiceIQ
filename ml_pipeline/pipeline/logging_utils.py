"""
Colored stage-tagged logger used across the whole project.

Usage:
    from pipeline.logging_utils import get_logger
    log = get_logger("OCR")
    log.info("Processed 3 pages")
    log.warning("Low confidence on page 2")

Output format:
    HH:MM:SS [LEVEL   ] [STAGE] - message

LEVEL is colored:
    DEBUG    -> cyan
    INFO     -> green
    WARNING  -> yellow
    ERROR    -> red
    CRITICAL -> bold magenta
"""
import logging
import os
import sys
from typing import Optional

# Enable ANSI escape sequences on Windows 10+ terminals (PowerShell, Windows Terminal).
if sys.platform == "win32":
    os.system("")

_RESET = "\033[0m"
_DIM = "\033[2m"
_BOLD_BLUE = "\033[1;94m"
_TIME = "\033[90m"

_LEVEL_COLORS = {
    "DEBUG":    "\033[36m",       # cyan
    "INFO":     "\033[32m",       # green
    "WARNING":  "\033[33m",       # yellow
    "ERROR":    "\033[31m",       # red
    "CRITICAL": "\033[1;35m",     # bold magenta
}


class _ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record, "%H:%M:%S")
        level = record.levelname
        color = _LEVEL_COLORS.get(level, "")
        stage = record.name
        msg = record.getMessage()
        return (
            f"{_TIME}{ts}{_RESET} "
            f"{color}[{level:<8}]{_RESET} "
            f"{_BOLD_BLUE}[{stage}]{_RESET} - {msg}"
        )


_LEVEL_FROM_ENV = os.environ.get("PS2_LOG_LEVEL", "INFO").upper()
_DEFAULT_LEVEL = getattr(logging, _LEVEL_FROM_ENV, logging.INFO)

_handler: Optional[logging.Handler] = None


def _ensure_root_handler() -> logging.Handler:
    """Install the colored handler exactly once on the ps2 root logger."""
    global _handler
    if _handler is not None:
        return _handler

    root = logging.getLogger("ps2")
    root.setLevel(_DEFAULT_LEVEL)
    root.propagate = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_ColoredFormatter())
    root.addHandler(handler)
    _handler = handler
    return handler


def get_logger(stage: str) -> logging.Logger:
    """
    Return a logger whose name is the bracketed stage tag.
    The handler is installed on the ps2 root so every stage shares one stream.
    """
    _ensure_root_handler()
    logger = logging.getLogger(f"ps2.{stage}")
    # Override the displayed name so the formatter shows just the stage.
    logger.name = stage
    logger.setLevel(_DEFAULT_LEVEL)
    return logger


def set_level(level: str) -> None:
    """Override the global log level at runtime."""
    lvl = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger("ps2").setLevel(lvl)


def configure_uvicorn() -> None:
    """
    Re-route uvicorn and FastAPI loggers through the colored formatter so the
    server startup banner and HTTP access lines use the same format as the
    pipeline logs.

    Without this, uvicorn keeps its own `INFO:     ...` handler and you see
    two different log styles in one stream. Call this once at API startup.
    """
    handler = _ensure_root_handler()
    targets = {
        "uvicorn":         "SERVER",
        "uvicorn.error":   "SERVER",
        "uvicorn.access":  "HTTP",
        "fastapi":         "SERVER",
    }
    for logger_name, stage in targets.items():
        lg = logging.getLogger(logger_name)
        lg.handlers = [handler]
        lg.name = stage
        lg.propagate = False
        lg.setLevel(_DEFAULT_LEVEL)
