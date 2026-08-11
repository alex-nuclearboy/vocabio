Requirements
============

Vocabio requires the following software for local development.

Python
------

The project supports Python 3.12, 3.13, and 3.14.

The repository contains a ``.python-version`` file that defines Python 3.13
as the preferred project runtime. The active interpreter must also satisfy
the Python requirement defined in ``pyproject.toml``.

Poetry
------

Python dependencies and the project environment are managed with Poetry.

The project currently uses Poetry 2.4.1.

Git
---

Git is required for source control and for working with the project
repository.

Docker
------

Docker with Docker Compose is required to run the local PostgreSQL service.

PostgreSQL does not need to be installed separately on the host system when
the Docker Compose development environment is used.

PostgreSQL
----------

Vocabio uses PostgreSQL as its database backend. The current local
development environment uses PostgreSQL 18 through Docker Compose.

The Django configuration accepts PostgreSQL database URLs only and does not
provide an SQLite fallback.

Verify the installed tools
--------------------------

Check that the required development tools are available:

.. code-block:: console

   git --version
   python --version
   poetry --version
   docker --version
   docker compose version
