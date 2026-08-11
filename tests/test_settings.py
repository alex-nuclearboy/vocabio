"""Tests for the Vocabio Django settings."""

# pylint: disable=redefined-outer-name

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest
from django.core.exceptions import ImproperlyConfigured

SETTINGS_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "settings.py"
)

VALID_DATABASE_URL = (
    "postgresql://user:pass@localhost:5432/vocabio"
)


def load_settings_module(
    monkeypatch,
    env_overrides: dict[str, str] | None = None,
) -> ModuleType:
    """Load the settings module with controlled environment values."""
    environment = {
        "DJANGO_SECRET_KEY": "test-secret-key",
        "DATABASE_URL": VALID_DATABASE_URL,
        "DATABASE_CONN_MAX_AGE": "0",
        "DATABASE_CONN_HEALTH_CHECKS": "False",
        "DATABASE_CONNECT_TIMEOUT": "5",
    }

    if env_overrides:
        environment.update(env_overrides)

    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    spec = importlib.util.spec_from_file_location(
        "settings_under_test",
        SETTINGS_PATH,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(
            "Unable to load the Django settings module."
        )

    module = importlib.util.module_from_spec(spec)

    try:
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)

    return module


@pytest.fixture()
def settings_module(monkeypatch):
    """Provide a freshly loaded settings module."""
    return load_settings_module(monkeypatch)


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------


class TestGetStrEnv:
    """Tests for string environment variable handling."""

    def test_returns_stripped_environment_value(
        self,
        monkeypatch,
        settings_module,
    ):
        """Return the value without surrounding whitespace."""
        monkeypatch.setenv(
            "VOCABIO_TEST_VALUE",
            "  custom value  ",
        )

        result = settings_module.get_str_env(
            "VOCABIO_TEST_VALUE",
            default="default",
        )

        assert result == "custom value"

    def test_returns_default_when_variable_is_missing(
        self,
        monkeypatch,
        settings_module,
    ):
        """Return the default when the variable is missing."""
        monkeypatch.delenv(
            "VOCABIO_TEST_VALUE",
            raising=False,
        )

        result = settings_module.get_str_env(
            "VOCABIO_TEST_VALUE",
            default="default",
        )

        assert result == "default"

    def test_returns_default_when_variable_is_empty(
        self,
        monkeypatch,
        settings_module,
    ):
        """Return the default when the variable is empty."""
        monkeypatch.setenv(
            "VOCABIO_TEST_VALUE",
            "   ",
        )

        result = settings_module.get_str_env(
            "VOCABIO_TEST_VALUE",
            default="default",
        )

        assert result == "default"


# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------


class TestBuildDatabaseConfig:
    """Tests for PostgreSQL database configuration."""

    def test_builds_valid_configuration(self, settings_module):
        """Build a complete PostgreSQL database configuration."""
        config = settings_module.build_database_config(
            database_url=VALID_DATABASE_URL,
            conn_max_age=60,
            conn_health_checks=True,
            connect_timeout=5,
        )

        assert config["ENGINE"] == "django.db.backends.postgresql"
        assert config["NAME"] == "vocabio"
        assert config["USER"] == "user"
        assert config["PASSWORD"] == "pass"
        assert config["HOST"] == "localhost"
        assert config["PORT"] == 5432
        assert config["CONN_MAX_AGE"] == 60
        assert config["CONN_HEALTH_CHECKS"] is True
        assert config["OPTIONS"]["connect_timeout"] == 5

    @pytest.mark.parametrize(
        "database_url",
        [
            "not-a-valid-url",
            "postgresql//user:pass@localhost:5432/vocabio",
        ],
    )
    def test_rejects_invalid_database_url(
        self,
        settings_module,
        database_url,
    ):
        """Reject malformed database URLs."""
        with pytest.raises(
            ImproperlyConfigured,
            match="DATABASE_URL has an invalid format",
        ):
            settings_module.build_database_config(
                database_url=database_url,
                conn_max_age=0,
                conn_health_checks=False,
                connect_timeout=5,
            )

    @pytest.mark.parametrize(
        "database_url",
        [
            "postgresql://user:pass@localhost:notaport/vocabio",
            "postgresql://user:pass@localhost:70000/vocabio",
        ],
    )
    def test_rejects_invalid_database_port(
        self,
        settings_module,
        database_url,
    ):
        """Reject database URLs with invalid port values."""
        with pytest.raises(
            ImproperlyConfigured,
            match="DATABASE_URL has an invalid format",
        ):
            settings_module.build_database_config(
                database_url=database_url,
                conn_max_age=0,
                conn_health_checks=False,
                connect_timeout=5,
            )

    @pytest.mark.parametrize(
        "database_url",
        [
            "sqlite:///db.sqlite3",
            "mysql://user:pass@localhost:3306/vocabio",
        ],
    )
    def test_rejects_non_postgresql_database(
        self,
        settings_module,
        database_url,
    ):
        """Reject database URLs that do not use PostgreSQL."""
        with pytest.raises(
            ImproperlyConfigured,
            match="DATABASE_URL must use PostgreSQL",
        ):
            settings_module.build_database_config(
                database_url=database_url,
                conn_max_age=0,
                conn_health_checks=False,
                connect_timeout=5,
            )

    @pytest.mark.parametrize(
        ("database_url", "missing_value"),
        [
            (
                "postgresql://user:pass@localhost:5432/",
                "database name",
            ),
            (
                "postgresql://:pass@localhost:5432/vocabio",
                "database user",
            ),
            (
                "postgresql://user@localhost:5432/vocabio",
                "database password",
            ),
            (
                "postgresql:///vocabio",
                "database host",
            ),
        ],
    )
    def test_rejects_missing_required_values(
        self,
        settings_module,
        database_url,
        missing_value,
    ):
        """Reject database URLs with missing required values."""
        with pytest.raises(
            ImproperlyConfigured,
            match=missing_value,
        ):
            settings_module.build_database_config(
                database_url=database_url,
                conn_max_age=0,
                conn_health_checks=False,
                connect_timeout=5,
            )

    def test_reports_multiple_missing_values(
        self,
        settings_module,
    ):
        """Report all missing database connection values."""
        with pytest.raises(
            ImproperlyConfigured,
            match="database user, database password",
        ):
            settings_module.build_database_config(
                database_url="postgresql://localhost:5432/vocabio",
                conn_max_age=0,
                conn_health_checks=False,
                connect_timeout=5,
            )

    def test_preserves_existing_database_options(
        self,
        settings_module,
    ):
        """Preserve database options when adding the timeout."""
        config = settings_module.build_database_config(
            database_url=(
                f"{VALID_DATABASE_URL}"
                "?options=-c%20search_path%3Dpublic"
            ),
            conn_max_age=0,
            conn_health_checks=False,
            connect_timeout=10,
        )

        assert config["OPTIONS"]["connect_timeout"] == 10
        assert len(config["OPTIONS"]) > 1


# ---------------------------------------------------------------------------
# Module-level validation
# ---------------------------------------------------------------------------


class TestModuleLevelValidation:
    """Tests for validation during settings initialisation."""

    def test_rejects_empty_secret_key(self, monkeypatch):
        """Reject an empty Django secret key."""
        with pytest.raises(
            ImproperlyConfigured,
            match="DJANGO_SECRET_KEY must not be empty",
        ):
            load_settings_module(
                monkeypatch,
                {
                    "DJANGO_SECRET_KEY": "   ",
                },
            )

    def test_rejects_empty_database_url(self, monkeypatch):
        """Reject an empty database URL."""
        with pytest.raises(
            ImproperlyConfigured,
            match="DATABASE_URL must not be empty",
        ):
            load_settings_module(
                monkeypatch,
                {
                    "DATABASE_URL": "   ",
                },
            )

    @pytest.mark.parametrize(
        "database_url",
        [
            (
                "postgresql://user:pass@"
                "${VOCABIO_MISSING_HOST}:5432/vocabio"
            ),
            (
                "postgresql://user:pass@"
                "$VOCABIO_MISSING_HOST:5432/vocabio"
            ),
        ],
    )
    def test_rejects_unresolved_environment_variable(
        self,
        monkeypatch,
        database_url,
    ):
        """Reject unresolved variables in the database URL."""
        monkeypatch.delenv(
            "VOCABIO_MISSING_HOST",
            raising=False,
        )

        with pytest.raises(
            ImproperlyConfigured,
            match="unresolved environment variables",
        ):
            load_settings_module(
                monkeypatch,
                {
                    "DATABASE_URL": database_url,
                },
            )

    def test_expands_database_environment_variables(
        self,
        monkeypatch,
    ):
        """Expand environment variables in the database URL."""
        monkeypatch.setenv(
            "VOCABIO_TEST_DB_HOST",
            "localhost",
        )

        module = load_settings_module(
            monkeypatch,
            {
                "DATABASE_URL": (
                    "postgresql://user:pass@"
                    "${VOCABIO_TEST_DB_HOST}:5432/vocabio"
                ),
            },
        )

        assert module.DATABASE_URL == VALID_DATABASE_URL
        assert module.DATABASES["default"]["HOST"] == "localhost"

    def test_rejects_negative_connection_max_age(
        self,
        monkeypatch,
    ):
        """Reject a negative database connection lifetime."""
        with pytest.raises(
            ImproperlyConfigured,
            match="DATABASE_CONN_MAX_AGE must not be negative",
        ):
            load_settings_module(
                monkeypatch,
                {
                    "DATABASE_CONN_MAX_AGE": "-1",
                },
            )

    def test_accepts_zero_connection_max_age(
        self,
        monkeypatch,
    ):
        """Accept zero as the database connection lifetime."""
        module = load_settings_module(
            monkeypatch,
            {
                "DATABASE_CONN_MAX_AGE": "0",
            },
        )

        assert module.DATABASE_CONN_MAX_AGE == 0
        assert module.DATABASES["default"]["CONN_MAX_AGE"] == 0

    def test_rejects_zero_connection_timeout(
        self,
        monkeypatch,
    ):
        """Reject a zero database connection timeout."""
        with pytest.raises(
            ImproperlyConfigured,
            match="DATABASE_CONNECT_TIMEOUT must be greater than zero",
        ):
            load_settings_module(
                monkeypatch,
                {
                    "DATABASE_CONNECT_TIMEOUT": "0",
                },
            )

    def test_rejects_negative_connection_timeout(
        self,
        monkeypatch,
    ):
        """Reject a negative database connection timeout."""
        with pytest.raises(
            ImproperlyConfigured,
            match="DATABASE_CONNECT_TIMEOUT must be greater than zero",
        ):
            load_settings_module(
                monkeypatch,
                {
                    "DATABASE_CONNECT_TIMEOUT": "-1",
                },
            )

    def test_applies_database_health_checks(
        self,
        monkeypatch,
    ):
        """Apply the configured database health-check setting."""
        module = load_settings_module(
            monkeypatch,
            {
                "DATABASE_CONN_HEALTH_CHECKS": "True",
            },
        )

        assert module.DATABASE_CONN_HEALTH_CHECKS is True
        assert (
            module.DATABASES["default"]["CONN_HEALTH_CHECKS"]
            is True
        )

    def test_applies_database_connection_timeout(
        self,
        monkeypatch,
    ):
        """Apply the configured database connection timeout."""
        module = load_settings_module(
            monkeypatch,
            {
                "DATABASE_CONNECT_TIMEOUT": "10",
            },
        )

        assert module.DATABASE_CONNECT_TIMEOUT == 10
        assert (
            module.DATABASES["default"]["OPTIONS"]["connect_timeout"]
            == 10
        )
