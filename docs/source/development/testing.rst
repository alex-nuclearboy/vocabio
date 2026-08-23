Testing
=======

Vocabio uses pytest as its test runner and pytest-django for Django
integration.

The test configuration is defined in ``pyproject.toml``. Local environment
setup is documented in
:doc:`../getting-started/local-development`.

Test configuration
------------------

pytest uses the Django settings module:

.. code-block:: text

   config.settings

Test modules follow the naming pattern:

.. code-block:: text

   test_*.py

This allows pytest to discover the project tests automatically.

Run the test suite
------------------

Run the complete test suite from the repository root:

.. code-block:: console

   poetry run pytest

A successful run must complete without test failures and must satisfy the
configured coverage threshold.

Run selected tests
------------------

A specific test module can be executed by passing its path to pytest:

.. code-block:: console

   poetry run pytest tests/test_settings.py

A subset of tests can also be selected with a pytest keyword expression:

.. code-block:: console

   poetry run pytest -k <expression>

Use targeted test runs while developing, but run the complete test suite
before committing substantial changes.

Django configuration
--------------------

pytest-django loads ``config.settings`` through the
``DJANGO_SETTINGS_MODULE`` configuration in ``pyproject.toml``.

Tests that exercise Django settings must control environment-dependent values
explicitly so that results do not depend on a developer's local
configuration.

The current configuration tests cover behaviour such as:

* environment variable handling;
* production host validation;
* CSRF trusted-origin normalisation;
* secure cookie requirements;
* HSTS configuration validation;
* PostgreSQL URL validation;
* invalid database URL formats and ports;
* accepted and rejected database schemes;
* missing database connection values;
* unresolved environment-variable references;
* database connection options;
* invalid numeric configuration values;
* unexpected database engine results.

Database-dependent tests
------------------------

A PostgreSQL database must be available before database-dependent tests are
run.

The current suite includes ``tests/test_database.py``, which opens a real
Django database connection, verifies that the configured backend is
PostgreSQL, and confirms that the connection is usable.

This test ensures that the project exercises the complete Django-to-PostgreSQL
connection path rather than validating database settings only.

The local PostgreSQL service and its health check are documented in
:doc:`../configuration/database`. Instructions for starting the local
database are available in
:doc:`../getting-started/local-development`.

The database integration test can be run independently with:

.. code-block:: console

   poetry run pytest tests/test_database.py

Tests that do not establish a database connection do not require the local
PostgreSQL service to be running.

Coverage
--------

Test coverage is collected automatically when the normal pytest command is
run:

.. code-block:: console

   poetry run pytest

The pytest configuration enables coverage reporting for the project source
packages and displays missing lines in the terminal.

The current coverage scope includes:

* ``config``;
* ``accounts``.

Branch coverage is enabled.

The following files and generated or test-only modules are excluded from
coverage measurement:

* ``config/asgi.py``;
* ``config/wsgi.py``;
* ``config/urls.py``;
* Django migration modules;
* test modules located inside application ``tests`` packages.

The configured minimum coverage threshold is:

.. code-block:: text

   90%

The test run fails when measured coverage falls below this threshold.

Coverage settings are maintained in ``pyproject.toml`` and should be updated
as the project structure expands.

Writing tests
-------------

Add tests with the code they verify.

Project-level tests for configuration and infrastructure are stored in the
top-level ``tests`` package. Application-specific tests are stored in a
``tests`` package inside the corresponding Django application.

For example:

.. code-block:: text

   tests/
   ├── test_database.py
   └── test_settings.py

   accounts/
   └── tests/
       └── __init__.py

Individual application test modules should be added only when corresponding
behaviour exists.

Test behaviour rather than implementation details where practical, and keep
individual tests focused on one expected outcome.

When testing configuration:

* provide environment values explicitly;
* cover both valid and invalid input;
* verify expected exceptions for rejected configuration;
* avoid depending on values from a developer's local ``.env`` file.

New behaviour should include corresponding tests whenever it can be verified
automatically.

Related documentation
---------------------

See also:

* :doc:`code-quality`
* :doc:`continuous-integration`
* :doc:`../getting-started/local-development`
* :doc:`../configuration/database`
