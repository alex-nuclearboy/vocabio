Project structure
=================

Vocabio follows a conventional Django project layout with project
configuration, automated tests, development tooling, documentation,
deployment configuration, and local infrastructure kept as separate
repository components.

The current project has the following structure:

.. code-block:: text

   vocabio/
   ├── .github/
   │   └── workflows/
   │       └── ci.yml
   ├── accounts/
   │   ├── migrations/
   │   │   └── __init__.py
   │   ├── tests/
   │   │   └── __init__.py
   │   ├── __init__.py
   │   ├── admin.py
   │   ├── apps.py
   │   ├── models.py
   │   └── views.py
   ├── config/
   │   ├── __init__.py
   │   ├── asgi.py
   │   ├── settings.py
   │   ├── urls.py
   │   └── wsgi.py
   ├── docs/
   │   ├── source/
   │   │   ├── configuration/
   │   │   ├── deployment/
   │   │   ├── development/
   │   │   ├── getting-started/
   │   │   ├── project/
   │   │   ├── reference/
   │   │   ├── conf.py
   │   │   └── index.rst
   │   ├── Makefile
   │   ├── README.md
   │   └── make.bat
   ├── tests/
   │   ├── __init__.py
   │   ├── test_database.py
   │   └── test_settings.py
   ├── .dockerignore
   ├── .env.example
   ├── .gitignore
   ├── .python-version
   ├── Dockerfile
   ├── LICENSE
   ├── README.md
   ├── compose.yaml
   ├── manage.py
   ├── poetry.lock
   └── pyproject.toml

The structure will expand as application-specific functionality is added.
This page should describe only components that are part of the repository
rather than anticipated future modules.

Project configuration
---------------------

The ``config`` package contains the Django project configuration.

The current foundation includes:

.. code-block:: text

   config/
   ├── __init__.py
   ├── asgi.py
   ├── settings.py
   ├── urls.py
   └── wsgi.py

``config/settings.py``
~~~~~~~~~~~~~~~~~~~~~~

Contains the Django settings and the project-specific configuration helpers.

Environment-specific and sensitive values are read from environment
variables rather than being stored directly in the module.

Environment variables are documented in
:doc:`../configuration/environment`, while PostgreSQL-specific configuration
and validation are documented in
:doc:`../configuration/database`.

The project-specific settings helpers are documented from their source
docstrings in :doc:`../reference/settings`.

``config/urls.py``
~~~~~~~~~~~~~~~~~~

Defines the root URL configuration for the Django project.

Application URL configurations can be included here as Django applications
are introduced.

``config/asgi.py``
~~~~~~~~~~~~~~~~~~

Exposes the ASGI application object used by ASGI-compatible servers.

``config/wsgi.py``
~~~~~~~~~~~~~~~~~~

Exposes the WSGI application object used by WSGI-compatible servers.

``config/__init__.py``
~~~~~~~~~~~~~~~~~~~~~~

Marks ``config`` as a Python package.

Accounts application
--------------------

The ``accounts`` package is the Django application for Vocabio-specific
account and authentication functionality.

Vocabio uses Django's built-in ``django.contrib.auth.User`` model and does
not define a custom user model.

The current application structure is:

.. code-block:: text

   accounts/
   ├── migrations/
   │   └── __init__.py
   ├── tests/
   │   └── __init__.py
   ├── __init__.py
   ├── admin.py
   ├── apps.py
   ├── models.py
   └── views.py

``accounts/apps.py`` defines the Django application configuration.

The ``admin.py``, ``models.py``, and ``views.py`` modules currently contain
no application-specific behaviour and will be extended only when the
corresponding functionality is introduced.

Application-specific tests are stored in ``accounts/tests``. Project-level
configuration and infrastructure tests remain in the top-level ``tests``
package.

Tests
-----

The top-level ``tests`` directory contains project-level tests for
configuration and infrastructure.

The current foundation includes:

.. code-block:: text

   tests/
   ├── __init__.py
   ├── test_database.py
   └── test_settings.py

``tests/test_database.py`` verifies real Django connectivity to PostgreSQL and
confirms that the configured connection uses the PostgreSQL backend.

``tests/test_settings.py`` verifies environment handling and project
configuration, including PostgreSQL database URL validation and related
settings behaviour.

The testing framework, test execution, and coverage requirements are
documented in :doc:`../development/testing`.

Application-specific tests are stored inside the corresponding application
package, while the top-level ``tests`` package remains responsible for
project-level configuration and infrastructure behaviour.

``tests/__init__.py``
~~~~~~~~~~~~~~~~~~~~~

Marks ``tests`` as a Python package.

Continuous integration
----------------------

The GitHub Actions workflow is stored in:

.. code-block:: text

   .github/workflows/ci.yml

It runs the primary project checks, Python compatibility checks, and the
production container build in isolated environments, using PostgreSQL service
containers where database access is required.

The workflow and its individual checks are documented in
:doc:`../development/continuous-integration`.

Documentation
-------------

Project documentation is maintained with Sphinx under ``docs``.

The documentation directory is organised as follows:

.. code-block:: text

   docs/
   ├── source/
   │   ├── configuration/
   │   ├── deployment/
   │   ├── development/
   │   ├── getting-started/
   │   ├── project/
   │   ├── reference/
   │   ├── conf.py
   │   └── index.rst
   ├── Makefile
   ├── README.md
   └── make.bat

``getting-started``
~~~~~~~~~~~~~~~~~~~

Contains the software requirements, installation procedure, and local
development workflow.

See :doc:`../getting-started/index`.

``configuration``
~~~~~~~~~~~~~~~~~

Documents environment variables and database configuration.

See :doc:`../configuration/index`.

``development``
~~~~~~~~~~~~~~~

Documents testing, code-quality checks, dependency auditing, and continuous
integration.

See :doc:`../development/index`.

``deployment``
~~~~~~~~~~~~~~

Documents the production container build, Koyeb deployment, Neon PostgreSQL
configuration, and routine deployment operations.

See :doc:`../deployment/index`.

``project``
~~~~~~~~~~~

Documents the repository structure and other project-level information.

See :doc:`index`.

Additional documentation sections should be introduced only when the
corresponding project components exist.

``reference``
~~~~~~~~~~~~~

Provides technical reference documentation generated from source-code
docstrings.

See :doc:`../reference/index`.

The ``docs`` directory also contains the Sphinx build wrappers and the
documentation README, while authored Sphinx pages are stored under
``docs/source``.

Environment template
--------------------

``.env.example`` is the template for local environment configuration.

It contains safe local defaults and empty placeholders for values that must
be provided locally. It must not contain real secrets.

The procedure for creating the local ``.env`` file is documented in
:doc:`../getting-started/local-development`.

The complete variable reference is available in
:doc:`../configuration/environment`.

Local infrastructure
--------------------

``compose.yaml`` defines the local Docker Compose infrastructure.

The current development environment uses it to run PostgreSQL without
requiring PostgreSQL to be installed directly on the host system.

Database configuration is documented in
:doc:`../configuration/database`, and the normal start and stop workflow is
documented in :doc:`../getting-started/local-development`.

Production container
--------------------

``Dockerfile`` defines the production container image used by the Koyeb
deployment.

The image uses a multi-stage build so that build tooling such as Poetry does
not remain in the final runtime image. Runtime dependencies are installed
from ``poetry.lock``, Django static files are collected during the build, and
Gunicorn runs the application as a non-root container user.

``.dockerignore`` limits the Docker build context and prevents local Secrets
and development artefacts from being copied into the production image.

The production container build is documented in
:doc:`../deployment/docker`, while Koyeb-specific deployment configuration is
documented in :doc:`../deployment/koyeb`.

Python runtime
--------------

``.python-version`` records Python 3.13 as the preferred local development and
primary CI runtime.

The production Dockerfile independently uses the Python 3.13 runtime series.
The two configurations should remain aligned.

The supported Python versions and development prerequisites are documented
in :doc:`../getting-started/requirements`.

Project metadata and dependencies
---------------------------------

``pyproject.toml`` is the central project configuration file.

It defines project metadata and dependencies and also contains configuration
for development tools, including pytest, coverage, and Pylint.

The relevant tool behaviour is documented separately:

* testing and coverage in :doc:`../development/testing`;
* static analysis and dependency auditing in
  :doc:`../development/code-quality`.

``poetry.lock`` records the resolved Python dependency versions used by
Poetry.

The lock file should remain consistent with ``pyproject.toml`` and should be
committed whenever dependency resolution changes.

Django management entry point
-----------------------------

``manage.py`` is the command-line entry point for Django management commands.

Common local commands include:

.. code-block:: console

   poetry run python manage.py check
   poetry run python manage.py migrate
   poetry run python manage.py runserver

The local development workflow is documented in
:doc:`../getting-started/local-development`.

Repository metadata
-------------------

``README.md``
~~~~~~~~~~~~~

Provides the repository-level introduction to Vocabio and serves as the main
entry point when the repository is viewed through the Git hosting service.

Detailed technical documentation belongs in ``docs`` rather than being
duplicated in the repository README.

``LICENSE``
~~~~~~~~~~~

Contains the licence terms under which the repository is distributed.

``.gitignore``
~~~~~~~~~~~~~~

Defines files and directories that Git must not track, including local or
generated development artefacts where applicable.

Sensitive local configuration such as ``.env`` must remain outside version
control.

Related documentation
---------------------

See also:

* :doc:`../getting-started/index`
* :doc:`../configuration/index`
* :doc:`../development/index`
* :doc:`../deployment/index`
* :doc:`../reference/index`
