"""Sphinx configuration for the Vocabio documentation."""

# pylint: disable=invalid-name,redefined-builtin
# pylint: disable=duplicate-code

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))


# Provide deterministic non-sensitive values for autodoc imports.
os.environ.update(
    {
        "DJANGO_SECRET_KEY": "documentation-only-secret-key",
        "DJANGO_DEBUG": "True",
        "DJANGO_ALLOWED_HOSTS": "localhost",
        "DJANGO_CSRF_TRUSTED_ORIGINS": "",
        "DJANGO_SECURE_SSL_REDIRECT": "False",
        "DJANGO_SESSION_COOKIE_SECURE": "False",
        "DJANGO_CSRF_COOKIE_SECURE": "False",
        "DJANGO_SECURE_HSTS_SECONDS": "0",
        "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS": "False",
        "DJANGO_SECURE_HSTS_PRELOAD": "False",
        "DATABASE_URL": (
            "postgresql://vocabio:vocabio@127.0.0.1:5432/vocabio"
        ),
        "DATABASE_CONN_MAX_AGE": "0",
        "DATABASE_CONN_HEALTH_CHECKS": "False",
        "DATABASE_CONNECT_TIMEOUT": "5",
        "DJANGO_LANGUAGE_CODE": "en-gb",
        "DJANGO_TIME_ZONE": "UTC",
    }
)


project = "Vocabio"
copyright = "2026, Alex"
author = "Alex"

extensions = [
    "sphinx.ext.autodoc",
]

exclude_patterns = []
