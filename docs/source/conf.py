"""Sphinx configuration for the Vocabio documentation."""

# pylint: disable=invalid-name,redefined-builtin

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
        "DATABASE_URL": (
            "postgresql://vocabio:vocabio@127.0.0.1:5432/vocabio"
        ),
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
