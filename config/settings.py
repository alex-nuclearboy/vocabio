"""Django settings for the Vocabio project.

Environment-specific and sensitive values are loaded from environment
variables. A local .env file is supported for development, while deployment
environment variables take precedence in production.
"""

import os
import re
from pathlib import Path
from urllib.parse import urlparse
from datetime import timedelta

import environ
from django.core.exceptions import ImproperlyConfigured

from config.logging import build_logging_config

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

env = environ.Env()

environ.Env.read_env(BASE_DIR / ".env")

DATABASE_ENV_REFERENCE_PATTERN = re.compile(
    r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}"
)


def expand_database_url(database_url: str) -> str:
    """Expand braced environment references in a database URL."""

    def replace_reference(match: re.Match[str]) -> str:
        variable_name = match.group(1)

        try:
            return os.environ[variable_name]
        except KeyError as exc:
            raise ImproperlyConfigured(
                "DATABASE_URL contains unresolved environment variables."
            ) from exc

    return DATABASE_ENV_REFERENCE_PATTERN.sub(
        replace_reference,
        database_url,
    )


def get_str_env(name: str, default: str) -> str:
    """Return a stripped environment variable or its default value."""
    return env(name, default=default).strip() or default


def build_database_config(
    database_url: str,
    conn_max_age: int,
    conn_health_checks: bool,
    connect_timeout: int,
) -> dict[str, object]:
    """Build and validate the Django PostgreSQL configuration."""
    try:
        parsed_url = urlparse(database_url)
        _ = parsed_url.port
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured(
            "DATABASE_URL has an invalid format."
        ) from exc

    if not parsed_url.scheme or "://" not in database_url:
        raise ImproperlyConfigured(
            "DATABASE_URL has an invalid format."
        )

    if parsed_url.scheme not in {
        "postgres",
        "postgresql",
        "psql",
        "pgsql",
    }:
        raise ImproperlyConfigured(
            "DATABASE_URL must use PostgreSQL."
        )

    database_config = environ.Env.db_url_config(database_url)

    if database_config.get("ENGINE") != "django.db.backends.postgresql":
        raise ImproperlyConfigured(
            "DATABASE_URL must use PostgreSQL."
        )

    required_values = {
        "NAME": "database name",
        "USER": "database user",
        "PASSWORD": "database password",
        "HOST": "database host",
    }

    missing_values = [
        description
        for key, description in required_values.items()
        if not database_config.get(key)
    ]

    if missing_values:
        missing = ", ".join(missing_values)

        raise ImproperlyConfigured(
            f"DATABASE_URL is missing: {missing}."
        )

    database_config["CONN_MAX_AGE"] = conn_max_age
    database_config["CONN_HEALTH_CHECKS"] = conn_health_checks
    database_config["DISABLE_SERVER_SIDE_CURSORS"] = (
        "-pooler" in (parsed_url.hostname or "")
    )

    database_options = database_config.get("OPTIONS") or {}

    database_options.setdefault(
        "connect_timeout",
        connect_timeout,
    )

    database_config["OPTIONS"] = database_options

    return database_config


# ---------------------------------------------------------------------------
# Core security settings
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "",
).strip()

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY must not be empty."
    )

DEBUG = env.bool(
    "DJANGO_DEBUG",
    default=False,
)

IS_PRODUCTION = not DEBUG

ALLOWED_HOSTS = [
    host.strip()
    for host in env.list(
        "DJANGO_ALLOWED_HOSTS",
        default=[],
    )
    if host.strip()
]

if IS_PRODUCTION and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS must be configured when "
        "DJANGO_DEBUG is False."
    )

if IS_PRODUCTION and "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "DJANGO_ALLOWED_HOSTS must not contain '*' in production."
    )

CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in env.list(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        default=[],
    )
    if origin.strip()
]

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_SSL_REDIRECT = env.bool(
    "DJANGO_SECURE_SSL_REDIRECT",
    default=False,
)

if IS_PRODUCTION and not SECURE_SSL_REDIRECT:
    raise ImproperlyConfigured(
        "DJANGO_SECURE_SSL_REDIRECT must be True in production."
    )

SESSION_COOKIE_SECURE = env.bool(
    "DJANGO_SESSION_COOKIE_SECURE",
    default=False,
)

CSRF_COOKIE_SECURE = env.bool(
    "DJANGO_CSRF_COOKIE_SECURE",
    default=False,
)

if IS_PRODUCTION and not SESSION_COOKIE_SECURE:
    raise ImproperlyConfigured(
        "DJANGO_SESSION_COOKIE_SECURE must be True in production."
    )

if IS_PRODUCTION and not CSRF_COOKIE_SECURE:
    raise ImproperlyConfigured(
        "DJANGO_CSRF_COOKIE_SECURE must be True in production."
    )

SECURE_HSTS_SECONDS = env.int(
    "DJANGO_SECURE_HSTS_SECONDS",
    default=0,
)

if SECURE_HSTS_SECONDS < 0:
    raise ImproperlyConfigured(
        "DJANGO_SECURE_HSTS_SECONDS must not be negative."
    )

SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=False,
)

SECURE_HSTS_PRELOAD = env.bool(
    "DJANGO_SECURE_HSTS_PRELOAD",
    default=False,
)


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "core.apps.CoreConfig",
    "accounts.apps.AccountsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASE_URL = env("DATABASE_URL").strip()

if not DATABASE_URL:
    raise ImproperlyConfigured(
        "DATABASE_URL must not be empty."
    )

DATABASE_URL = expand_database_url(DATABASE_URL)

DATABASE_CONN_MAX_AGE = env.int(
    "DATABASE_CONN_MAX_AGE",
    default=0,
)

if DATABASE_CONN_MAX_AGE < 0:
    raise ImproperlyConfigured(
        "DATABASE_CONN_MAX_AGE must not be negative."
    )

DATABASE_CONN_HEALTH_CHECKS = env.bool(
    "DATABASE_CONN_HEALTH_CHECKS",
    default=False,
)

DATABASE_CONNECT_TIMEOUT = env.int(
    "DATABASE_CONNECT_TIMEOUT",
    default=5,
)

if DATABASE_CONNECT_TIMEOUT <= 0:
    raise ImproperlyConfigured(
        "DATABASE_CONNECT_TIMEOUT must be greater than zero."
    )

DATABASES = {
    "default": build_database_config(
        database_url=DATABASE_URL,
        conn_max_age=DATABASE_CONN_MAX_AGE,
        conn_health_checks=DATABASE_CONN_HEALTH_CHECKS,
        connect_timeout=DATABASE_CONNECT_TIMEOUT,
    ),
}


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

CLIENT_IP_META_PRECEDENCE_ORDER = (
    "HTTP_X_FORWARDED_FOR",
    "REMOTE_ADDR",
)

CLIENT_IP_PROXY_ORDER = "right-most"

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AXES_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_RESET_ON_SUCCESS = True
AXES_RESET_COOL_OFF_ON_FAILURE_DURING_LOCKOUT = False

AXES_LOCKOUT_PARAMETERS = [
    ["username", "ip_address"],
]

AXES_LOCKOUT_CALLABLE = "accounts.security.login_lockout_response"

AXES_IPWARE_META_PRECEDENCE_ORDER = (
    CLIENT_IP_META_PRECEDENCE_ORDER
)
AXES_IPWARE_PROXY_ORDER = CLIENT_IP_PROXY_ORDER

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"


# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = get_str_env(
    "DJANGO_LANGUAGE_CODE",
    default="en-gb",
)

TIME_ZONE = get_str_env(
    "DJANGO_TIME_ZONE",
    default="UTC",
)

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOGGING = build_logging_config(
    base_dir=BASE_DIR,
    debug=DEBUG,
)
