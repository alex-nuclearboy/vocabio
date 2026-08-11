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

The CI job runs on the current GitHub-hosted Ubuntu environment.

The job has a timeout of 15 minutes.

Python
~~~~~~

The workflow reads the Python version from:

.. code-block:: text

   .python-version

Using the same repository-controlled runtime prevents the CI Python version
from being maintained separately from the project configuration.

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

The CI job starts an isolated PostgreSQL service container based on:

.. code-block:: text

   postgres:18-alpine

The service creates a database and role using CI-only credentials.

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

The CI workflow performs the following steps in order.

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
