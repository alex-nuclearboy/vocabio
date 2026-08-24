"""Logging configuration for the Vocabio project."""

from pathlib import Path
from typing import Any


LOCAL_LOG_MAX_BYTES = 5 * 1024 * 1024
LOCAL_LOG_BACKUP_COUNT = 3

PLAIN_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

COLOUR_LOG_FORMAT = (
    "%(asctime)s | "
    "%(log_color)s%(levelname)-8s%(reset)s | "
    "%(name)s | %(message)s"
)

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_COLOURS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}


def build_logging_config(
    base_dir: Path,
    debug: bool,
) -> dict[str, Any]:
    """Build the Django logging configuration."""
    console_formatter = "colour" if debug else "plain"

    handlers: dict[str, dict[str, Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG" if debug else "INFO",
            "formatter": console_formatter,
        },
    }

    active_handlers = ["console"]

    if debug:
        log_directory = base_dir / "logs"
        log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "plain",
            "filename": str(log_directory / "vocabio.log"),
            "maxBytes": LOCAL_LOG_MAX_BYTES,
            "backupCount": LOCAL_LOG_BACKUP_COUNT,
            "encoding": "utf-8",
            "delay": True,
        }

        active_handlers.append("file")

    application_level = "DEBUG" if debug else "INFO"
    django_level = "INFO" if debug else "WARNING"
    axes_level = "INFO" if debug else "WARNING"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": PLAIN_LOG_FORMAT,
                "datefmt": LOG_DATE_FORMAT,
            },
            "colour": {
                "()": "colorlog.ColoredFormatter",
                "format": COLOUR_LOG_FORMAT,
                "datefmt": LOG_DATE_FORMAT,
                "log_colors": LOG_COLOURS,
            },
        },
        "handlers": handlers,
        "root": {
            "handlers": list(active_handlers),
            "level": "WARNING",
        },
        "loggers": {
            "django": {
                "handlers": list(active_handlers),
                "level": django_level,
                "propagate": False,
            },
            "axes": {
                "handlers": list(active_handlers),
                "level": axes_level,
                "propagate": False,
            },
            "accounts": {
                "handlers": list(active_handlers),
                "level": application_level,
                "propagate": False,
            },
            "core": {
                "handlers": list(active_handlers),
                "level": application_level,
                "propagate": False,
            },
            "infrastructure": {
                "handlers": list(active_handlers),
                "level": application_level,
                "propagate": False,
            },
            "vocabio.audit": {
                "handlers": list(active_handlers),
                "level": "INFO",
                "propagate": False,
            },
        },
    }
