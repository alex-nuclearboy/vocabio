Deployment operations
=====================

Overview
--------

This guide covers routine operational tasks after the Vocabio application,
Koyeb Web Service, and Neon PostgreSQL database have been configured.

It documents:

* access to the running Koyeb Service;
* production database migrations;
* creation and maintenance of the Django superuser;
* controlled Django management commands;
* Service redeployment;
* deployment and runtime logs;
* post-deployment verification;
* common operational checks.

Initial Koyeb configuration is documented in :doc:`koyeb`.

The Neon database, application role, and pooled and direct connection
strategy are documented in :doc:`neon`.

Before you begin
----------------

Complete the Neon and Koyeb deployment configuration before using the
procedures in this guide.

The running Service should provide:

.. code-block:: text

   DATABASE_URL
   DIRECT_DATABASE_URL

``DATABASE_URL`` contains the pooled Neon connection used by the normal
Django web process.

``DIRECT_DATABASE_URL`` contains the direct Neon connection reserved for
migrations and other controlled database operations.

Do not print either value to the terminal, application logs, or
documentation.

Koyeb CLI access
----------------

Remote Django management commands are executed on a running Koyeb Instance
with the Koyeb CLI.

Install the CLI by following the official `Koyeb CLI installation`_ guide.

Authenticate with an API token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the Koyeb control panel, open ``Settings``, select the ``API`` tab, and
choose ``Create API token``.

Provide a descriptive name and description for the token, create it, and
copy its value immediately. The token value cannot be retrieved again after
leaving the page.

Authenticate the CLI:

.. code-block:: console

   koyeb login

Paste the API token when prompted.

Verify the authenticated account and active Koyeb organisation:

.. code-block:: console

   koyeb whoami

The API token is a credential. Do not commit it to the repository, add it
to environment files, include it in documentation, or expose it in logs.

If a token is exposed, revoke it through the Koyeb control panel and create
a replacement.

Identify the App and Service
----------------------------

List the Apps available to the authenticated Koyeb organisation:

.. code-block:: console

   koyeb apps list

Identify the App that contains the Vocabio deployment and use its exact
name as ``<app>``.

List the Services belonging to that App:

.. code-block:: console

   koyeb services list --app <app>

Identify the Vocabio Web Service and use its exact name as ``<service>``.

The examples below use ``<app>`` and ``<service>`` as placeholders for
these values.

Open a Service shell
--------------------

Open an interactive shell in an Instance belonging to the Web Service:

.. code-block:: console

   koyeb services exec <service> /bin/sh --app <app>

Koyeb selects an available Instance belonging to the Service and opens the
shell in its runtime environment.

If no Instance is available
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the shell cannot be opened because the Free Instance has scaled to zero,
send an HTTP/1.1 request to an existing public Vocabio route and allow the
Service to start before retrying the command.

On Windows PowerShell, for example:

.. code-block:: console

   curl.exe -i --http1.1 https://<public-domain>/admin/

On Linux or macOS:

.. code-block:: console

   curl -i --http1.1 https://<public-domain>/admin/

Replace ``<public-domain>`` with the actual Koyeb public domain of the
Service.

The request is used only to wake the Service. A ``302 Found`` response
redirecting to ``/admin/login/`` is expected for an unauthenticated request
and confirms that the Service is responding.

The active Instances can be inspected with:

.. code-block:: console

   koyeb instances list --app <app> --service <service>

Instance identifiers can change when the Service restarts, scales to zero,
or is redeployed, so do not store them in deployment documentation.

For troubleshooting that requires a specific Instance, Koyeb also supports
opening a shell by Instance ID:

.. code-block:: console

   koyeb instances exec <instance-id> /bin/sh

Routine Vocabio management commands should normally use
``koyeb services exec`` so that a specific Instance identifier does not need
to be selected manually.

After the shell opens, inspect the current directory:

.. code-block:: console

   pwd
   ls

Confirm that the application directory contains ``manage.py`` before
running Django management commands.

Before performing a database operation, confirm that the direct connection
variable is available without displaying its value:

.. code-block:: console

   test -n "$DIRECT_DATABASE_URL" && echo "Direct database URL is available"

If the command produces no output, stop and verify the Service environment
configuration before continuing.

Apply production migrations
---------------------------

Production migrations must use the direct Neon connection.

Do not change the Service-wide ``DATABASE_URL`` value. Override it only for
the individual management command.

From the remote Service shell, inspect the migration plan:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py migrate --plan

Apply the migrations:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py migrate

After the command completes, verify the migration state:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py showmigrations

The normal Gunicorn process continues to use the pooled connection from
``DATABASE_URL`` throughout this procedure.

Do not add ``migrate`` to the Koyeb Build command, Run command, or
``Procfile``. Schema changes are controlled release operations rather than
application startup tasks.

Subsequent schema changes
~~~~~~~~~~~~~~~~~~~~~~~~~

For the initial release, apply migrations after the first successful Koyeb
deployment.

For later releases, choose the deployment and migration order according to
the compatibility of the code and schema change. Where possible, design
migrations so that the previous and new application versions can tolerate
the transition during deployment.

Review potentially destructive or incompatible migrations before applying
them.

For significant schema changes, verify the migration plan before modifying
production data.

Check for unapplied migrations
------------------------------

To check whether the deployed code has unapplied migrations, run:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py migrate --check

A zero exit status means that all migrations known to the deployed
application are applied.

Create the production superuser
-------------------------------

Create the production superuser only after the initial migrations have
completed successfully.

From the remote Service shell, run:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py createsuperuser

Follow the interactive prompts.

Do not place the superuser password in Koyeb environment variables,
Secrets, repository files, or deployment documentation.

The superuser is an application account stored in the Vocabio database. It
should not be created through the Neon Console.

Change a superuser password
---------------------------

To change the password of an existing Django user, run:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py changepassword <user>

Enter the new password interactively.

Run other Django management commands
------------------------------------

Use the same temporary database substitution for controlled management
commands that modify or inspect production database state:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py <command>

Do not export the direct URL over the whole shell session unless there is a
specific operational reason to do so.

Keeping the override on the individual command makes it clear which process
uses the direct connection and reduces the risk of accidentally changing
the normal runtime connection behaviour.

After completing the required management commands, exit the remote shell:

.. code-block:: console

   exit

Redeploy the Service
--------------------

Git-driven deployments normally occur automatically when changes are pushed
or merged into the configured deployment branch.

A manual redeployment can be started from the Koyeb control panel when the
same source revision needs to be deployed again.

The Koyeb CLI can also redeploy a Service:

.. code-block:: console

   koyeb services redeploy <service> --app <app> --wait

The ``--wait`` option keeps the command attached until the deployment
finishes or the CLI timeout is reached.

A configuration change to the Service also creates a new Deployment.

Redeploy after changing production environment variables or Secret
references so that the new configuration is applied to running Instances.

Review deployment logs
----------------------

Build and runtime logs are available from the Koyeb control panel.

The Koyeb CLI can also read Service logs.

Follow runtime logs:

.. code-block:: console

   koyeb services logs <service> --app <app> --type runtime --tail

Follow build logs:

.. code-block:: console

   koyeb services logs <service> --app <app> --type build --tail

Do not enable debug options that expose sensitive values when collecting
logs for troubleshooting.

Verify a deployment
-------------------

After a deployment and any required migrations, verify that:

* the Deployment reaches a healthy running state;
* Gunicorn starts without runtime errors;
* the public ``.koyeb.app`` HTTPS domain responds;
* HTTPS redirection does not loop;
* Django static files are served correctly;
* ``/admin/`` loads successfully;
* database-backed pages can read and write expected data;
* no migration errors appear in the runtime logs.

The application root can return ``404 Not Found`` until Vocabio defines a
root URL. A working ``/admin/`` page and normal application routes are
sufficient to confirm that this specific response is not a deployment
failure.

Verify database connectivity
----------------------------

The running application uses the pooled Neon connection.

Open a Service shell as described above. To verify the pooled database
connection used by the running application, open a connection through
Django without displaying its credentials:

.. code-block:: console

   python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('Database connection OK')"

For migration-specific verification, use the direct connection:

.. code-block:: console

   DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py migrate --check

Do not print ``DATABASE_URL`` or ``DIRECT_DATABASE_URL`` while
troubleshooting connectivity.

Troubleshooting
---------------

Build failure
~~~~~~~~~~~~~

Review the Koyeb build logs first.

Confirm that:

* the expected Git revision was deployed;
* the Python buildpack detected the project;
* dependencies installed from the Poetry lock file;
* automatic ``collectstatic`` completed successfully;
* no custom Koyeb Build command duplicates the buildpack steps.

Runtime startup failure
~~~~~~~~~~~~~~~~~~~~~~~

Review the runtime logs and confirm that:

* the ``Procfile`` web process was detected;
* Gunicorn started successfully;
* ``PORT`` is supplied by Koyeb;
* required production environment variables are present;
* referenced Secrets exist and are accessible to the Service.

Database connection failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Confirm that the Neon project is active and that the Service configuration
contains both database variables.

The web application should use:

.. code-block:: text

   DATABASE_URL

Controlled schema operations should use:

.. code-block:: text

   DIRECT_DATABASE_URL

Verify that the pooled connection targets ``vocabiodb`` with
``vocabio_owner`` and that the direct connection targets the same database
and role without the pooled endpoint.

Static-file failure
~~~~~~~~~~~~~~~~~~~

Review the build log and confirm that ``collectstatic`` completed during the
build.

Check that WhiteNoise remains configured in Django and that the generated
``staticfiles/`` directory is not expected to exist in the Git repository.

Redirect loop
~~~~~~~~~~~~~

If the public URL redirects repeatedly, verify the proxy-aware Django
security configuration and the Koyeb HTTPS settings documented in
:doc:`koyeb`.

Do not disable production cookie security as a workaround for a proxy or
redirect configuration error.

Slow first request
~~~~~~~~~~~~~~~~~~

A slow first request after inactivity can be expected when the Koyeb Free
Instance and the Neon compute have both suspended.

The Koyeb Service can need time to start its Instance, while Neon can need
time to wake the database compute.

Check logs and resource status before treating a single cold-start delay as
an application failure.

Operational safety
------------------

Before running a production management command:

* confirm the active Koyeb account and organisation;
* confirm the target App and Service;
* review the command before execution;
* use ``DIRECT_DATABASE_URL`` only for the intended command;
* avoid displaying credentials;
* verify the result before leaving the remote shell.

Do not perform destructive database operations without an appropriate
backup and recovery procedure.

Database dumps, restores, and recovery workflows should use the direct Neon
connection and should be documented separately once the backup strategy is
defined.

Official references
-------------------

The following official pages provide the platform documentation used by
these procedures:

* `Koyeb CLI installation`_
* `Koyeb CLI reference`_
* `Koyeb troubleshooting`_
* `Koyeb Deployments`_
* `Koyeb environment variables`_
* `Koyeb Secrets`_
* `Koyeb Instances`_
* `Neon connection pooling`_

.. _Koyeb CLI installation:
   https://www.koyeb.com/docs/build-and-deploy/cli/installation
.. _Koyeb CLI reference:
   https://www.koyeb.com/docs/build-and-deploy/cli/reference
.. _Koyeb troubleshooting:
   https://www.koyeb.com/docs/build-and-deploy/troubleshooting-tips
.. _Koyeb Deployments:
   https://www.koyeb.com/docs/reference/deployments
.. _Koyeb environment variables:
   https://www.koyeb.com/docs/build-and-deploy/environment-variables
.. _Koyeb Secrets:
   https://www.koyeb.com/docs/reference/secrets
.. _Koyeb Instances:
   https://www.koyeb.com/docs/reference/instances
.. _Neon connection pooling:
   https://neon.com/docs/connect/connection-pooling

.. note::

   Koyeb and Neon can change CLI commands, service behaviour, and platform
   interfaces. Check the linked official documentation if the available
   controls or command syntax differ from this guide.
