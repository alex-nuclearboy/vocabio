Code quality
============

Vocabio uses automated static analysis, Django system checks, migration
consistency checks, dependency auditing, and the test suite to maintain code
quality.

The commands in this document are intended to be run from the repository
root.

Run the following checks before committing substantial changes.

Poetry validation
-----------------

Validate the project metadata and Poetry configuration:

.. code-block:: console

   poetry check

This verifies the project configuration defined in ``pyproject.toml``.

Static analysis
---------------

Vocabio uses Pylint with pylint-django for static analysis.

Run Pylint with:

.. code-block:: console

   poetry run pylint config accounts tests manage.py docs/source/conf.py

The Pylint configuration is maintained in ``pyproject.toml``.

The current configuration:

* loads ``pylint-django``;
* uses ``config.settings`` as the Django settings module;
* targets the project's minimum supported Python version;
* ignores migration directories;
* enforces a maximum line length of 79 characters;
* reports duplicated code according to the configured similarity threshold.

The local Pylint command includes each Django application source directory
alongside the project configuration, project-level tests, management entry
point, and Sphinx configuration. Keep the local command and continuous
integration aligned as new applications are added.

Code formatting
---------------

The project intentionally does not use an automatic code formatter.

Source formatting is maintained manually, while Pylint is used to identify
code-quality and correctness issues.

New and modified Python code should follow the existing project style,
including the configured maximum line length.

Django system checks
--------------------

Run Django's system check framework with:

.. code-block:: console

   poetry run python manage.py check

The command validates the Django project configuration and reports detected
configuration or application problems.

A PostgreSQL service must be available when a system check requires a
database connection. Local database setup is documented in
:doc:`../getting-started/local-development`.

Migration consistency
---------------------

Check that model changes are represented by committed Django migrations:

.. code-block:: console

   poetry run python manage.py makemigrations --check --dry-run

The command exits with a non-zero status if Django detects model changes
that require new migrations. It does not create migration files.

Static-file collection
----------------------

Verify production static-file processing with:

.. code-block:: console

   poetry run python manage.py collectstatic --noinput

The command exercises the configured static-file storage and WhiteNoise
manifest processing. The generated ``staticfiles/`` directory is excluded
from version control.

Test suite
----------

Run the complete test suite with:

.. code-block:: console

   poetry run pytest

Coverage enforcement is applied automatically through the pytest
configuration.

Testing behaviour and coverage configuration are documented in
:doc:`testing`.

Dependency auditing
-------------------

Vocabio uses ``pip-audit`` to check installed Python packages for known
vulnerabilities.

Run the dependency audit with:

.. code-block:: console

   poetry run python -m pip_audit --local

The audit examines the packages installed in the current Poetry environment.

Review reported vulnerabilities before updating or suppressing affected
dependencies. Dependency changes should remain consistent with
``pyproject.toml`` and ``poetry.lock``.

Documentation validation
------------------------

Build the Sphinx documentation with strict warning and cross-reference
checking:

.. code-block:: console

   poetry run sphinx-build -E -a -W -n -T -b html docs/source docs/_build/html

The command performs a clean documentation build and fails if Sphinx reports
a warning, an unresolved reference, or a build error.

The generated HTML files are written to ``docs/_build/html``.

Production container validation
-------------------------------

When changing the Dockerfile, ``.dockerignore``, runtime dependencies, or
deployment configuration, build the production image locally with:

.. code-block:: console

   docker build --tag vocabio:local .

The production image build is also validated automatically by continuous
integration.

A Docker image build is not required before every routine source-code commit.
The standard local quality-check sequence remains unchanged.

The production container is documented in
:doc:`../deployment/docker`.

Recommended check sequence
--------------------------

The complete local quality-check sequence is:

.. code-block:: console

   poetry check
   poetry run python -m pip_audit --local
   poetry run pylint config accounts tests manage.py docs/source/conf.py
   poetry run python manage.py check
   poetry run python manage.py makemigrations --check --dry-run
   poetry run python manage.py collectstatic --noinput
   poetry run pytest
   poetry run sphinx-build -E -a -W -n -T -b html docs/source docs/_build/html

These checks correspond to the primary local validation performed by
continuous integration. Production container validation is run separately
when relevant and is always performed by CI.

The Django development server does not need to be running while these
commands are executed.

Related documentation
---------------------

See also:

* :doc:`testing`
* :doc:`continuous-integration`
* :doc:`../getting-started/local-development`
