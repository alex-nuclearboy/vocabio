Production container
====================

Overview
--------

Vocabio uses a repository ``Dockerfile`` to define the production container
image deployed on Koyeb.

The Dockerfile controls the Python runtime, Poetry version, production
dependency installation, static-file collection, runtime user, and Gunicorn
process.

Docker is used for the production build environment. It does not replace the
standard local development workflow, where Django runs from the Poetry
environment on the host and PostgreSQL runs through Docker Compose.

Container structure
-------------------

The production image uses a multi-stage build.

The builder stage:

* uses Python 3.13;
* installs Poetry 2.4.1;
* installs only the main dependency group from ``poetry.lock``;
* copies the application source;
* runs Django static-file collection.

The runtime stage:

* uses the same Python runtime family;
* receives the prepared application and virtual environment;
* does not include Poetry;
* runs as the non-root ``vocabio`` user;
* starts Gunicorn.

Python runtime
--------------

The production container uses:

.. code-block:: text

   python:3.13-slim-trixie

The Python 3.13 series matches the preferred project runtime recorded in
``.python-version``.

The Docker image tag keeps the Python minor version and Debian distribution
stable while allowing supported Python 3.13 patch releases to be incorporated
when the base image is rebuilt.

Poetry
------

The builder stage installs:

.. code-block:: text

   Poetry 2.4.1

This matches the Poetry version used by local development and continuous
integration.

Poetry is required only while constructing the application environment. It is
not copied into the final runtime image.

Production dependencies
-----------------------

The builder installs the locked runtime dependencies with:

.. code-block:: console

   poetry sync --only main --no-root --no-ansi

Development dependencies are not installed in the production image.

The committed ``poetry.lock`` file remains the source of resolved Python
dependency versions.

Static files
------------

Django static files are collected while the image is built.

The Dockerfile provides non-sensitive build-only Django settings so that
``config.settings`` can be initialised without exposing production Secrets.

The build uses production-mode Django settings so that local development
file logging is not enabled while static files are collected.

The build runs:

.. code-block:: console

   python manage.py collectstatic --noinput

The generated ``staticfiles`` directory is copied into the final runtime
image and served by WhiteNoise.

The static-file build does not require a connection to the production Neon
database.

Runtime user
------------

The final image runs the application as the dedicated non-root ``vocabio``
user.

The application does not require root privileges at runtime.

Runtime process
---------------

The image starts Gunicorn and binds it to all container interfaces.

The runtime command uses the Koyeb ``PORT`` environment variable when it is
available and falls back to port ``8000`` otherwise.

The runtime process is defined by the Dockerfile ``CMD``. No Koyeb command
override is required.

Database operations
-------------------

Database migrations are not executed while the image is built and are not
part of the container startup command.

The normal web process uses the pooled Neon connection supplied through
``DATABASE_URL``.

Controlled production migration and administration commands use the direct
Neon connection supplied through ``DIRECT_DATABASE_URL``.

Production database operations are documented in :doc:`operations`.

Build context
-------------

The repository ``.dockerignore`` file excludes local Secrets, development
artefacts, tests, documentation, Docker Compose configuration, and other
files that are not required by the production image.

In particular, the local ``.env`` file must never be copied into the
production image.

Local runtime logs under ``logs/`` are also excluded from the Docker build
context and are not included in the production image.

Local image validation
----------------------

Build the production image locally from the repository root with:

.. code-block:: console

   docker build --tag vocabio:local .

The image can be inspected without starting the Django web application:

.. code-block:: console

   docker run --rm --entrypoint python vocabio:local --version
   docker run --rm --entrypoint gunicorn vocabio:local --version
   docker run --rm --entrypoint id vocabio:local

The normal local Django workflow continues to use Poetry directly and does
not require the application itself to run inside a container.

Related documentation
---------------------

See also:

* :doc:`koyeb`
* :doc:`neon`
* :doc:`operations`
* :doc:`../getting-started/local-development`
* :doc:`../development/continuous-integration`
