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
   │   ├── templates/
   │   │   └── accounts/
   │   │       └── login.html
   │   ├── tests/
   │   │   ├── __init__.py
   │   │   ├── test_forms.py
   │   │   ├── test_lockout.py
   │   │   ├── test_urls.py
   │   │   └── test_views.py
   │   ├── __init__.py
   │   ├── admin.py
   │   ├── apps.py
   │   ├── forms.py
   │   ├── models.py
   │   ├── urls.py
   │   └── views.py
   ├── core/
   │   ├── migrations/
   │   │   └── __init__.py
   │   ├── tests/
   │   │   ├── __init__.py
   │   │   ├── test_urls.py
   │   │   └── test_views.py
   │   ├── views/
   │   │   ├── __init__.py
   │   │   ├── health.py
   │   │   └── home.py
   │   ├── __init__.py
   │   ├── admin.py
   │   ├── apps.py
   │   ├── models.py
   │   └── urls.py
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
   │   ├── assertions.py
   │   ├── test_authentication_settings.py
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

The package currently contains:

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

It also defines the project authentication configuration, including
authentication backends, login-attempt protection, the login route, and the
named login and logout redirect destinations.

Authentication behaviour and access-control policy are documented in
:doc:`authentication`.

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

The current root configuration includes the ``core`` and ``accounts`` URL
namespaces at the application root and exposes Django Admin under
``/admin/``.

``config/asgi.py``
~~~~~~~~~~~~~~~~~~

Exposes the ASGI application object used by ASGI-compatible servers.

``config/wsgi.py``
~~~~~~~~~~~~~~~~~~

Exposes the WSGI application object used by WSGI-compatible servers.

``config/__init__.py``
~~~~~~~~~~~~~~~~~~~~~~

Marks ``config`` as a Python package.

Core application
----------------

The ``core`` package is the Django application responsible for project-level
HTTP behaviour that does not belong to a domain-specific application.

The current application structure is:

.. code-block:: text

   core/
   ├── migrations/
   │   └── __init__.py
   ├── tests/
   │   ├── __init__.py
   │   ├── test_urls.py
   │   └── test_views.py
   ├── views/
   │   ├── __init__.py
   │   ├── health.py
   │   └── home.py
   ├── __init__.py
   ├── admin.py
   ├── apps.py
   ├── models.py
   └── urls.py

``core/apps.py`` defines the Django application configuration.

``core/urls.py`` defines the namespaced public home, liveness, and readiness
routes.

``core/views/home.py`` provides the public application root.

``core/views/health.py`` provides separate liveness and readiness endpoints.
The liveness endpoint reports whether the Django application process can
respond without accessing the database. The readiness endpoint additionally
verifies access to the configured PostgreSQL database.

``core/admin.py`` and ``core/models.py`` currently contain no
application-specific behaviour. They remain part of the standard Django
application structure for future project-level models and Admin
configuration if required.

Application-specific tests are stored in ``core/tests``. They cover URL
configuration, home-page availability, HTTP method restrictions, health
responses, database availability, and health-response cache behaviour.

The current health endpoints are application-level endpoints. The production
Koyeb Service continues to use its existing platform health-check
configuration unless that deployment policy is changed separately.

Accounts application
--------------------

The ``accounts`` package is the Django application responsible for
Vocabio-specific authentication functionality.

Vocabio uses Django's built-in ``django.contrib.auth.User`` model and does
not define a custom user model.

The current application structure is:

.. code-block:: text

   accounts/
   ├── migrations/
   │   └── __init__.py
   ├── templates/
   │   └── accounts/
   │       └── login.html
   ├── tests/
   │   ├── __init__.py
   │   ├── test_forms.py
   │   ├── test_lockout.py
   │   ├── test_urls.py
   │   └── test_views.py
   ├── __init__.py
   ├── admin.py
   ├── apps.py
   ├── forms.py
   ├── models.py
   ├── urls.py
   └── views.py

``accounts/apps.py`` defines the Django application configuration.

``accounts/forms.py`` defines the Vocabio login form. The form subclasses
Django's standard ``AuthenticationForm`` and configures the username and
password fields for the Vocabio authentication interface.

``accounts/urls.py`` defines the namespaced login and logout routes.

``accounts/views.py`` implements login and logout behaviour using Django's
standard authentication and session framework. Login supports validated
local ``next`` redirects, while logout accepts ``POST`` requests only.

``accounts/templates/accounts/login.html`` contains the current login page.
The form uses CSRF protection, displays form validation errors, and preserves
a validated local redirect target when one is supplied.

``accounts/admin.py`` and ``accounts/models.py`` currently contain no
application-specific behaviour. The application uses Django's built-in user
model rather than defining an account model of its own.

Application-specific tests are stored in ``accounts/tests``. They cover the
login form, URL configuration, authentication views, redirect safety, CSRF
behaviour, cache-control behaviour, session behaviour, inactive-user
rejection, login-attempt lockout behaviour, client IP handling, and Django
Admin lockout protection.

Detailed authentication behaviour and the project authorisation policy are
documented in :doc:`authentication`.

Tests
-----

The top-level ``tests`` directory contains project-level tests for
configuration and infrastructure, together with shared test support code.

The current project-level test package contains:

.. code-block:: text

   tests/
   ├── __init__.py
   ├── assertions.py
   ├── test_authentication_settings.py
   ├── test_database.py
   └── test_settings.py

``tests/assertions.py`` contains reusable assertions shared by application
test suites.

``tests/test_authentication_settings.py`` verifies the project-level
authentication routing, redirect settings, authentication backends, lockout
policy, and client IP resolution configuration.

``tests/test_database.py`` verifies real Django connectivity to PostgreSQL
and confirms that the configured connection uses the PostgreSQL backend.

``tests/test_settings.py`` verifies environment handling and project
configuration, including PostgreSQL database URL validation and related
settings behaviour.

The testing framework, test execution, and coverage requirements are
documented in :doc:`../development/testing`.

Application-specific tests are stored inside the corresponding application
package, while the top-level ``tests`` package contains project-level
configuration and infrastructure tests together with shared test support.

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
