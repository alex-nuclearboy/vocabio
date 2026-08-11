Code quality
============

Vocabio uses automated static analysis, Django system checks, dependency
auditing, and the test suite to maintain code quality.

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

   poetry run pylint config tests manage.py

The Pylint configuration is maintained in ``pyproject.toml``.

The current configuration:

* loads ``pylint-django``;
* uses ``config.settings`` as the Django settings module;
* targets the project's configured Python version;
* ignores migration directories;
* enforces a maximum line length of 79 characters;
* reports duplicated code according to the configured similarity threshold.

As new Django applications are added, include their source directories in
the local Pylint command and in continuous integration.

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

Recommended check sequence
--------------------------

The complete local quality-check sequence is:

.. code-block:: console

   poetry check
   poetry run python -m pip_audit --local
   poetry run pylint config tests manage.py
   poetry run python manage.py check
   poetry run pytest

These checks correspond to the principal checks performed by continuous
integration.

The Django development server does not need to be running while these
commands are executed.

Related documentation
---------------------

See also:

* :doc:`testing`
* :doc:`continuous-integration`
* :doc:`../getting-started/local-development`
