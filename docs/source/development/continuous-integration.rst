Continuous integration
======================

Vocabio uses GitHub Actions to run automated project checks in a clean
environment.

The workflow is defined in:

.. code-block:: text

   .github/workflows/ci.yml

Workflow triggers
-----------------

The CI workflow runs for:

* pushes to the ``main`` branch;
* pull requests.

Concurrent runs for the same Git reference are grouped together. When a
newer run starts, an obsolete in-progress run for the same group is
cancelled.

The workflow has read-only access to repository contents.

Runtime environment
-------------------

The CI workflow runs on GitHub-hosted Ubuntu environments.

The primary ``checks`` job has a timeout of 15 minutes. The Python
compatibility jobs and the ``container-build`` job have a timeout of 10
minutes each.

Python
~~~~~~

The primary ``checks`` job reads the preferred Python version from:

.. code-block:: text

   .python-version

The project currently uses Python 3.13 as its preferred development and
primary CI runtime.

A separate compatibility matrix verifies the other supported Python
versions:

* Python 3.12;
* Python 3.14.

Together, the primary and compatibility jobs verify the supported Python
3.12, 3.13, and 3.14 range declared by the project.

Poetry
~~~~~~

The workflow installs the project's pinned Poetry version with ``pipx``.

The current CI configuration uses:

.. code-block:: text

   Poetry 2.4.1

Dependency caching is handled by the Python setup action using
``poetry.lock`` as the cache dependency path.

PostgreSQL service
------------------

The primary ``checks`` job and Python compatibility jobs start isolated
PostgreSQL service containers based on:

.. code-block:: text

   postgres:18-alpine

Each service creates a database and role using CI-only credentials.

A PostgreSQL health check runs with ``pg_isready``. GitHub Actions waits for
the service to become healthy before database-dependent project commands are
executed.

The CI database is independent of the local development database.

Database configuration and validation behaviour are documented in
:doc:`../configuration/database`.

CI environment variables
------------------------

The workflow defines environment values required to initialise Django and the
PostgreSQL connection during CI.

These values are used only by the CI environment and must not contain local
or deployment credentials.

The workflow provides values for:

* ``DJANGO_SECRET_KEY``;
* ``DJANGO_DEBUG``;
* ``DJANGO_ALLOWED_HOSTS``;
* ``DJANGO_CSRF_TRUSTED_ORIGINS``;
* ``DJANGO_SECURE_SSL_REDIRECT``;
* ``DJANGO_SESSION_COOKIE_SECURE``;
* ``DJANGO_CSRF_COOKIE_SECURE``;
* ``DJANGO_SECURE_HSTS_SECONDS``;
* ``DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS``;
* ``DJANGO_SECURE_HSTS_PRELOAD``;
* ``DATABASE_URL``;
* ``DATABASE_CONN_MAX_AGE``;
* ``DATABASE_CONN_HEALTH_CHECKS``;
* ``DATABASE_CONNECT_TIMEOUT``;
* ``DJANGO_LANGUAGE_CODE``;
* ``DJANGO_TIME_ZONE``.

The meaning and application defaults of these variables are documented in
:doc:`../configuration/environment`.

Workflow checks
---------------

The primary ``checks`` job performs the following steps in order.

Repository checkout
~~~~~~~~~~~~~~~~~~~

The repository is checked out into the GitHub Actions runner.

Poetry installation
~~~~~~~~~~~~~~~~~~~

The configured Poetry version is installed with ``pipx``.

Python setup
~~~~~~~~~~~~

Python is configured from ``.python-version`` and the Poetry dependency cache
is enabled.

Poetry configuration validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The workflow validates the project configuration with:

.. code-block:: console

   poetry check

Dependency installation
~~~~~~~~~~~~~~~~~~~~~~~

Application and development dependencies are installed from the locked
project configuration:

.. code-block:: console

   poetry install --with dev --no-interaction --no-root --no-ansi

Dependency audit
~~~~~~~~~~~~~~~~

Installed Python dependencies are checked for known vulnerabilities:

.. code-block:: console

   poetry run python -m pip_audit --local

Static analysis
~~~~~~~~~~~~~~~

Pylint runs against the current project source, tests, and Sphinx
configuration.

The CI invocation uses GitHub-compatible output formatting so that reported
issues can be surfaced by the workflow interface.

Local static-analysis configuration is documented in
:doc:`code-quality`.

Django system checks
~~~~~~~~~~~~~~~~~~~~

The workflow runs:

.. code-block:: console

   poetry run python manage.py check

Migration consistency
~~~~~~~~~~~~~~~~~~~~~

The primary CI job checks that model changes are represented by committed
Django migrations:

.. code-block:: console

   poetry run python manage.py makemigrations --check --dry-run

The command fails if Django detects model changes that require new
migrations. It does not create migration files during CI.

Static-file collection
~~~~~~~~~~~~~~~~~~~~~~

The workflow verifies production static-file processing with:

.. code-block:: console

   poetry run python manage.py collectstatic --noinput

This exercises the configured Django static-file storage and WhiteNoise
manifest processing before the test suite is executed.

Test suite
~~~~~~~~~~

The workflow runs the complete test suite with:

.. code-block:: console

   poetry run pytest

Coverage collection and the minimum coverage threshold are applied through
the pytest configuration in ``pyproject.toml``.

Testing and coverage are documented in :doc:`testing`.

Documentation build
~~~~~~~~~~~~~~~~~~~

The workflow performs a clean Sphinx HTML build with strict warning and
cross-reference checking:

.. code-block:: console

   poetry run sphinx-build -E -a -W -n -T -b html docs/source docs/_build/html

The CI run fails if the documentation produces a Sphinx warning, contains an
unresolved reference, or cannot be built successfully.

Python compatibility checks
---------------------------

A separate ``python-compatibility`` job verifies the supported Python
versions that are not used by the primary ``checks`` job.

The compatibility matrix currently runs on:

* Python 3.12;
* Python 3.14.

For each version, the workflow:

* checks out the repository;
* installs Poetry;
* configures the selected Python version;
* installs the project and development dependencies;
* runs Django system checks;
* runs the complete test suite with coverage.

Python 3.13 is not repeated in this matrix because it is already exercised
by the primary ``checks`` job through ``.python-version``.

Production container build
--------------------------

A separate ``container-build`` job validates the production Dockerfile.

The job:

* checks out the repository;
* builds the production image from the root ``Dockerfile``;
* verifies that Python and Gunicorn are available in the final image;
* verifies that the container runs as the expected non-root user;
* verifies that collected static files are present;
* verifies that Poetry is not included in the runtime image.

The build runs:

.. code-block:: console

   docker build --tag vocabio:ci .

This verifies the same production container definition used by Koyeb without
requiring deployment credentials or a connection to the production database.

The Docker build installs Poetry 2.4.1 inside its builder stage, installs only
the runtime dependencies from ``poetry.lock``, and runs Django static-file
collection.

The image validation checks the final runtime stage rather than the temporary
builder stage.

The production container architecture is documented in
:doc:`../deployment/docker`.

Relationship to local checks
----------------------------

Continuous integration does not replace local validation.

Run the checks documented in :doc:`code-quality` before committing
substantial changes. This shortens the feedback cycle and reduces avoidable
CI failures.

The CI environment is intentionally isolated from local development. A
successful local run does not depend on CI credentials, and CI must not
depend on secrets stored in a developer's local ``.env`` file.

Related documentation
---------------------

See also:

* :doc:`testing`
* :doc:`code-quality`
* :doc:`../configuration/environment`
* :doc:`../configuration/database`
* :doc:`../getting-started/local-development`
