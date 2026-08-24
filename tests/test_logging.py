"""Tests for the Vocabio logging configuration."""

from config.logging import (
    LOCAL_LOG_BACKUP_COUNT,
    LOCAL_LOG_MAX_BYTES,
    LOG_COLOURS,
    build_logging_config,
)


def test_development_logging_uses_coloured_console(tmp_path):
    """Development logging uses coloured console output."""
    config = build_logging_config(
        base_dir=tmp_path,
        debug=True,
    )

    console = config["handlers"]["console"]

    assert console["level"] == "DEBUG"
    assert console["formatter"] == "colour"


def test_development_logging_uses_rotating_file(tmp_path):
    """Development logging writes to a rotating local file."""
    config = build_logging_config(
        base_dir=tmp_path,
        debug=True,
    )

    file_handler = config["handlers"]["file"]

    assert file_handler["class"] == (
        "logging.handlers.RotatingFileHandler"
    )
    assert file_handler["level"] == "DEBUG"
    assert file_handler["formatter"] == "plain"
    assert file_handler["maxBytes"] == LOCAL_LOG_MAX_BYTES
    assert (
        file_handler["backupCount"]
        == LOCAL_LOG_BACKUP_COUNT
    )
    assert file_handler["encoding"] == "utf-8"
    assert file_handler["delay"] is True
    assert file_handler["filename"] == str(
        tmp_path / "logs" / "vocabio.log"
    )


def test_development_logging_creates_log_directory(tmp_path):
    """Development logging prepares the local log directory."""
    build_logging_config(
        base_dir=tmp_path,
        debug=True,
    )

    assert (tmp_path / "logs").is_dir()


def test_production_logging_uses_plain_console_only(tmp_path):
    """Production logging avoids persistent container log files."""
    config = build_logging_config(
        base_dir=tmp_path,
        debug=False,
    )

    console = config["handlers"]["console"]

    assert console["level"] == "INFO"
    assert console["formatter"] == "plain"
    assert "file" not in config["handlers"]
    assert not (tmp_path / "logs").exists()


def test_development_application_loggers_use_debug_level(tmp_path):
    """Application loggers expose debug output during development."""
    config = build_logging_config(
        base_dir=tmp_path,
        debug=True,
    )

    for logger_name in (
        "accounts",
        "core",
        "infrastructure",
    ):
        assert config["loggers"][logger_name]["level"] == "DEBUG"


def test_production_application_loggers_use_info_level(tmp_path):
    """Application loggers retain informational events in production."""
    config = build_logging_config(
        base_dir=tmp_path,
        debug=False,
    )

    for logger_name in (
        "accounts",
        "core",
        "infrastructure",
    ):
        assert config["loggers"][logger_name]["level"] == "INFO"


def test_framework_logging_is_quieter_in_production(tmp_path):
    """Framework loggers use warning level in production."""
    config = build_logging_config(
        base_dir=tmp_path,
        debug=False,
    )

    assert config["loggers"]["django"]["level"] == "WARNING"
    assert config["loggers"]["axes"]["level"] == "WARNING"


def test_audit_logging_remains_enabled_at_info_level(tmp_path):
    """Audit events remain enabled regardless of debug mode."""
    development = build_logging_config(
        base_dir=tmp_path / "development",
        debug=True,
    )
    production = build_logging_config(
        base_dir=tmp_path / "production",
        debug=False,
    )

    assert (
        development["loggers"]["vocabio.audit"]["level"]
        == "INFO"
    )
    assert (
        production["loggers"]["vocabio.audit"]["level"]
        == "INFO"
    )


def test_log_levels_use_expected_colours():
    """Console log levels use the project colour convention."""
    assert LOG_COLOURS["DEBUG"] == "cyan"
    assert LOG_COLOURS["INFO"] == "green"
    assert LOG_COLOURS["WARNING"] == "yellow"
    assert LOG_COLOURS["ERROR"] == "red"
    assert LOG_COLOURS["CRITICAL"] == "bold_red"
