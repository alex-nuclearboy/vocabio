Database configuration
======================

Vocabio uses PostgreSQL as its only database backend.

The current local development environment runs PostgreSQL 18 through Docker
Compose. Local startup instructions are documented in
:doc:`../getting-started/local-development`.

Database URL
------------

Django reads its database connection from ``DATABASE_URL``.

The local development value is assembled in ``.env`` from the PostgreSQL
container settings:

.. code-block:: text

   DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

Environment-variable references are expanded before the URL is validated and
converted to a Django database configuration.

Accepted schemes
----------------

The database URL must use one of the supported PostgreSQL URL schemes:

* ``postgres``;
* ``postgresql``;
* ``psql``;
* ``pgsql``.

Any URL that resolves to a database backend other than
``django.db.backends.postgresql`` is rejected.

Required connection values
--------------------------

The resolved database configuration must contain:

* a database name;
* a database user;
* a database password;
* a database host.

A missing required value causes application configuration to fail with
``ImproperlyConfigured``.

URL validation
--------------

Vocabio validates ``DATABASE_URL`` before the database configuration is used.

Configuration fails when:

* ``DATABASE_URL`` is empty;
* the URL format is invalid;
* the port is invalid;
* the URL does not use an accepted PostgreSQL scheme;
* the resulting Django database engine is not PostgreSQL;
* a required connection value is missing;
* an environment-variable reference remains unresolved.

Both ``$VARIABLE`` and ``${VARIABLE}`` references are considered unresolved
if they remain in the expanded URL.

Connection lifetime
-------------------

``DATABASE_CONN_MAX_AGE`` controls the lifetime of persistent database
connections in seconds.

The default value is:

.. code-block:: text

   0

Negative values are rejected.

Connection health checks
------------------------

``DATABASE_CONN_HEALTH_CHECKS`` controls Django database connection health
checks.

The default value is:

.. code-block:: text

   False

Connection timeout
------------------

``DATABASE_CONNECT_TIMEOUT`` defines how long Django waits while opening a
PostgreSQL connection.

The default value is:

.. code-block:: text

   5

The value is expressed in seconds and must be greater than zero.

When the database URL already defines database options, the project preserves
those options. The configured ``connect_timeout`` is added only when that
option is not already present.

Production database connections
-------------------------------

The deployed application uses Neon PostgreSQL 18.

The production environment has two database connection strings:

* a pooled connection exposed as ``DATABASE_URL``;
* a direct connection exposed as ``DIRECT_DATABASE_URL``.

The normal Django application reads only ``DATABASE_URL``. The deployed
Koyeb Web Service therefore uses the pooled Neon connection for normal web
traffic.

``DIRECT_DATABASE_URL`` is not a second Django database alias and is not
read automatically by ``config/settings.py``. It is reserved for migrations
and other controlled production database operations.

For an administrative command, the direct connection is substituted for
``DATABASE_URL`` only for that process:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py <command>

The current production connection settings are:

.. code-block:: text

   DATABASE_CONN_MAX_AGE=30
   DATABASE_CONN_HEALTH_CHECKS=True
   DATABASE_CONNECT_TIMEOUT=5

The pooled and direct Neon connection strings target the same production
branch, database, and role. The pooled hostname contains ``-pooler``, while
the direct hostname does not.

Do not reconstruct or edit Neon connection strings manually. Keep all
connection parameters supplied by Neon.

The Neon project and connection-string setup are documented in
:doc:`../deployment/neon`. Production management commands are documented in
:doc:`../deployment/operations`.

Docker Compose database
-----------------------

The local PostgreSQL service is named ``postgres`` and uses the
``postgres:18-alpine`` image.

Docker Compose publishes the configured host port on the IPv4 loopback
interface only and maps it to PostgreSQL port ``5432`` inside the container.
The database service is therefore not exposed through other host network
interfaces.

Database data is stored in the named ``postgres_data`` volume.

The service health check uses ``pg_isready``. Database-dependent Django
commands and tests should be run only after the service reports a healthy
status.

The local PostgreSQL service can be started with:

.. code-block:: console

   docker compose up -d postgres

Its status can be checked with:

.. code-block:: console

   docker compose ps

These commands are included here for reference. The complete local workflow
is documented in :doc:`../getting-started/local-development`.

Related configuration
---------------------

For the complete Django environment-variable reference, see
:doc:`environment`.

For the production Neon configuration, see :doc:`../deployment/neon`.

For production database operations, see
:doc:`../deployment/operations`.
