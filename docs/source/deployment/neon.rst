Neon PostgreSQL
===============

Overview
--------

Vocabio uses Neon as the managed PostgreSQL service for the deployed
application.

This guide documents the Neon project configuration used by Vocabio,
including the application database and role, connection pooling, secret
handling, and the separation between runtime and administrative database
connections.

The deployment uses:

* PostgreSQL 18;
* the ``production`` branch;
* the ``Primary`` read-write compute;
* the ``vocabiodb`` database;
* the ``vocabio_owner`` Postgres role;
* a pooled connection for the Django web application;
* a direct connection for migrations and other controlled database
  operations.

General Django environment variables are documented in
:doc:`../configuration/environment`. Database URL validation is documented
in :doc:`../configuration/database`.

Before you begin
----------------

A Neon account and organisation are required. If they do not already exist,
create them through the `Neon Console`_.

The procedure below begins with the Neon project used by Vocabio. If a
suitable project already exists, review its settings and continue from the
relevant step instead of creating another project.

Current account, plan, and onboarding information is available in the
official `Neon documentation`_ and `Neon pricing`_ pages.


Create or configure the Vocabio project
---------------------------------------

Create a Neon project for Vocabio, or verify that an existing project uses
the required settings.

Use:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Setting
     - Value
   * - Project name
     - ``Vocabio``
   * - Postgres version
     - ``18``
   * - Region
     - ``AWS Europe Central 1 (Frankfurt)``
   * - Neon Auth
     - Disabled

PostgreSQL 18 is selected to match the PostgreSQL major version used by the
local Docker Compose environment. Keeping the local and hosted environments
on the same major version reduces avoidable differences during development
and deployment.

The Frankfurt region is used for this deployment. Keeping the application
and database geographically close reduces avoidable network latency.

Choose the region carefully because an existing Neon project cannot be
moved to another region in place.

Keep Neon Auth disabled. Vocabio uses Django authentication and sessions,
and application authorisation is based on Django's permission framework,
so Neon Auth is not part of this deployment.

If the project is being created now, select ``Create project`` and continue
to the project dashboard.

Review the project resources
----------------------------

Use the ``production`` branch for the deployed application.

The project should provide:

* the ``production`` branch;
* the ``Primary`` read-write compute;
* the default ``neondb`` database;
* the default ``neondb_owner`` role.

Keep the default database and role unchanged. Vocabio creates its own
application role and database in the next steps.

No additional branch or compute is required for the current deployment.

Review the Free plan
--------------------

The current Vocabio deployment can operate within the Neon Free plan limits.

A paid plan is not required for the expected low-traffic workload, but
current limits and pricing should be reviewed before deployment because Neon
can change plan allowances and service behaviour.

Current Free plan allowances include:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Resource
     - Allowance
   * - Price
     - ``$0``
   * - Payment card
     - Not required
   * - Projects
     - Up to 100
   * - Compute
     - 100 CU-hours per project each month
   * - Maximum compute size
     - Up to 2 CU
   * - Storage
     - 0.5 GB per project
   * - Included branches
     - 10 per project
   * - Automatic suspension
     - After five minutes of inactivity
   * - Restore window
     - Up to six hours or 1 GB of data changes
   * - Monitoring history
     - One day
   * - Public network transfer
     - 5 GB per month

A CU-hour measures compute consumption rather than one hour of application
availability. For a single compute endpoint:

.. code-block:: text

   CU-hours = average compute size in CU × active time in hours

Compute usage is counted only while the database is active. After the
configured idle period, the Free plan can suspend the compute endpoint.
A new database connection wakes it again, so the first request after an
idle period can take slightly longer.

This brief cold start is expected behaviour and does not indicate data loss.

Monitor compute, storage, and network transfer usage in the Neon Console.
The limited restore window is not a replacement for an independent backup
and recovery strategy.

Create the application role
---------------------------

Make sure that the ``production`` branch is selected.

In the Neon Console sidebar, under ``Postgres database``:

#. open ``Roles``;
#. select ``Add role``;
#. enter ``vocabio_owner`` as the role name;
#. select ``Create``.

Neon generates a credential for the role. Treat it as a production secret.

Do not store the generated credential in the repository, documentation,
``.env.example``, issue trackers, logs, or screenshots.

Keep the automatically created ``neondb_owner`` role unchanged.

The ``vocabio_owner`` role provides explicit application ownership and
separate application credentials. Roles created through the Neon Console
use Neon's managed role privileges and should not be described as strict
least-privilege roles.

If stricter privilege isolation is required in the future, create and grant
a more restricted Postgres role explicitly.

Create the application database
-------------------------------

Make sure that the ``production`` branch is still selected.

In the Neon Console sidebar, under ``Postgres database``:

#. open ``Databases``;
#. select ``Add database``;
#. enter ``vocabiodb`` as the database name;
#. select ``vocabio_owner`` as the owner;
#. select ``Create``.

Keep the automatically created ``neondb`` database unchanged.

The production application uses ``vocabiodb`` with ``vocabio_owner`` as its
owner.

Prepare the connection strings
------------------------------

Vocabio uses two Neon connection strings generated from the same branch,
compute, database, and role.

.. list-table::
   :header-rows: 1
   :widths: 20 45 35

   * - Connection
     - Purpose
     - Application use
   * - Pooled
     - Running Django web application
     - ``DATABASE_URL``
   * - Direct
     - Migrations, dumps, restores, and controlled database operations
     - ``DIRECT_DATABASE_URL``

Both connection strings contain database credentials and must be handled as
secrets.

Select the connection target
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From the project dashboard, open ``Connect`` and select:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Setting
     - Value
   * - Branch
     - ``production``
   * - Compute
     - ``Primary``
   * - Database
     - ``vocabiodb``
   * - Role
     - ``vocabio_owner``

The ``Connect`` widget generates a connection string for the selected
branch, database, and role.

Copy the pooled connection
~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable ``Connection pooling``.

Copy the complete connection string. The pooled hostname contains
``-pooler``.

Store this value as a Koyeb Secret. The running web service exposes that
Secret to Django as:

.. code-block:: text

   DATABASE_URL

The pooled connection is the normal production connection used by the
deployed application.

Copy the direct connection
~~~~~~~~~~~~~~~~~~~~~~~~~~

Disable ``Connection pooling`` without changing the selected branch,
compute, database, or role.

Copy the complete connection string again. The direct hostname does not
contain ``-pooler``.

Store the direct value as a separate Koyeb Secret and expose it to the
Service as ``DIRECT_DATABASE_URL``.

Django does not use this variable for its normal database configuration. It
is reserved for migrations, dumps, restores, and other controlled database
operations.

Connection string integrity
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Keep all query parameters supplied by Neon, including SSL-related
parameters such as ``sslmode`` and any channel-binding settings present in
the generated URL.

Do not reconstruct, shorten, or edit either connection string manually.

Do not save either connection string in:

* ``.env``;
* ``.env.example``;
* Git;
* GitHub issues;
* application logs;
* screenshots;
* repository documentation.

Pooled and direct connections
-----------------------------

Neon implements connection pooling with PgBouncer.

The pooled URL is intended for normal application traffic. Its hostname
contains ``-pooler``.

The direct URL connects without the PgBouncer endpoint. It should be used
for schema migrations and other operations that rely on session-level
database behaviour.

The Koyeb Web Service receives the pooled connection as ``DATABASE_URL`` and
the direct connection as ``DIRECT_DATABASE_URL``.

The Django settings module uses only ``DATABASE_URL`` for its configured
database connection. For a controlled database operation, temporarily run
the command with ``DATABASE_URL`` set to ``DIRECT_DATABASE_URL`` for that
process only.

This keeps the normal application runtime on the pooled connection without
adding a second permanent Django database alias.

Store the database credentials on Koyeb
---------------------------------------

Production database credentials are stored as Koyeb Secrets rather than
committed configuration values.

Store the pooled and direct Neon URLs as separate Koyeb Secrets.

The web service maps the pooled Secret to ``DATABASE_URL`` and the direct
Secret to ``DIRECT_DATABASE_URL``.

Although ``DIRECT_DATABASE_URL`` is present in the Service environment, it
is reserved for controlled database operations.

The exact Secret names are deployment configuration and do not affect the
Django settings contract.

For Neon-specific guidance on connecting a database to a Koyeb deployment,
see `Use Neon with Koyeb`_.

Django connection settings
--------------------------

The project validates ``DATABASE_URL`` as a PostgreSQL URL before creating
the Django database configuration.

The production service uses the following database connection settings:

.. code-block:: text

   DATABASE_CONN_MAX_AGE=30
   DATABASE_CONN_HEALTH_CHECKS=True
   DATABASE_CONNECT_TIMEOUT=5

``DATABASE_CONN_MAX_AGE`` keeps eligible database connections open for up to
30 seconds in the production service, ``DATABASE_CONN_HEALTH_CHECKS``
enables connection health checks, and ``DATABASE_CONNECT_TIMEOUT`` limits
the time allowed to establish a database connection.

The general environment-variable contract is documented in
:doc:`../configuration/environment`.

Database URL parsing and validation are documented in
:doc:`../configuration/database`.

Verify the Neon configuration
-----------------------------

Before continuing to the Koyeb deployment, confirm that:

* the ``production`` branch is selected;
* PostgreSQL 18 is used by the project;
* ``Primary`` is the selected compute;
* ``vocabiodb`` exists on the ``production`` branch;
* ``vocabio_owner`` owns ``vocabiodb``;
* both connection strings target ``production``, ``vocabiodb``, and
  ``vocabio_owner``;
* the pooled hostname contains ``-pooler``;
* the direct hostname does not contain ``-pooler``;
* all query parameters supplied by Neon remain present;
* the pooled connection is mapped to ``DATABASE_URL`` on Koyeb;
* the direct connection is mapped to ``DIRECT_DATABASE_URL`` on Koyeb;
* no database credentials are committed to the repository.

Operational notes
-----------------

Do not run production migrations or create the production superuser from
the Neon Console.

Database schema changes should be applied through Django management
commands using the direct Neon connection.

Monitor Free plan resource usage in the Neon Console. If the application
approaches storage, compute, or network-transfer limits, reduce usage or
move the project to an appropriate paid plan before those limits become an
operational problem.

The Free plan restore window should not be treated as a replacement for a
separate backup and recovery strategy.

Official references
-------------------

The following official pages provide the current platform documentation:

* `Neon documentation`_
* `Tour the Neon Console`_
* `Neon pricing`_
* `Neon plans`_
* `Postgres compatibility`_
* `Manage projects`_
* `Manage computes`_
* `Manage roles`_
* `Manage databases`_
* `Connection pooling`_
* `Use Neon with Koyeb`_
* `Network transfer`_
* `Neon changelog`_
* `Koyeb Secrets`_
* `Koyeb environment variables`_

.. _Neon website: https://neon.com/
.. _Neon Console: https://console.neon.tech/
.. _Neon documentation: https://neon.com/docs/introduction
.. _Tour the Neon Console: https://neon.com/docs/get-started/signing-up
.. _Neon pricing: https://neon.com/pricing
.. _Neon plans: https://neon.com/docs/introduction/plans
.. _Postgres compatibility: https://neon.com/docs/reference/compatibility
.. _Manage projects: https://neon.com/docs/manage/projects
.. _Manage computes: https://neon.com/docs/manage/endpoints
.. _Manage roles: https://neon.com/docs/manage/roles
.. _Manage databases: https://neon.com/docs/manage/databases
.. _Connection pooling: https://neon.com/docs/connect/connection-pooling
.. _Use Neon with Koyeb: https://neon.com/docs/guides/koyeb
.. _Network transfer: https://neon.com/docs/introduction/network-transfer
.. _Neon changelog: https://neon.com/docs/changelog
.. _Koyeb Secrets: https://www.koyeb.com/docs/reference/secrets
.. _Koyeb environment variables:
   https://www.koyeb.com/docs/build-and-deploy/environment-variables

.. note::

   Neon can change Console labels, plan limits, pricing, and service
   behaviour. If the interface differs from this procedure, check the
   official documentation linked above before proceeding.
