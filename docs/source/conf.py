"""Sphinx configuration for the Vocabio documentation."""

# pylint: disable=invalid-name,redefined-builtin

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(PROJECT_ROOT))


# Provide non-sensitive values required when autodoc imports Django settings.
os.environ.setdefault(
    "DJANGO_SECRET_KEY",
    "documentation-only-secret-key",
)
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://vocabio:vocabio@127.0.0.1:5432/vocabio",
)


project = "Vocabio"
copyright = "2026, Alex"
author = "Alex"

extensions = [
    "sphinx.ext.autodoc",
]

exclude_patterns = []
