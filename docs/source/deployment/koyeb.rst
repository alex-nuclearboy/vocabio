Koyeb deployment
================

Overview
--------

Vocabio uses Koyeb to build and run the hosted Django web application.

This guide documents the Koyeb Service configuration used by Vocabio,
including GitHub deployment, the Dockerfile builder, the Gunicorn runtime
process, production environment variables, Koyeb Secrets, and deployment
verification.

The deployment uses:

* a Koyeb Web Service;
* a GitHub repository as the deployment source;
* the ``main`` branch as the deployed branch;
* the Dockerfile builder;
* the repository ``Dockerfile`` as the production image definition;
* Gunicorn as the production WSGI server;
* WhiteNoise for collected static files;
* Neon PostgreSQL for the application database;
* Koyeb Secrets for sensitive production values;
* the Koyeb-provided public domain for Django host, CSRF, and HTTP
  health-check configuration.

The Neon database configuration is documented in :doc:`neon`.

General Django environment variables are documented in
:doc:`../configuration/environment`.

Before you begin
----------------

A Koyeb account and organisation are required. If they do not already
exist, create them through the `Koyeb control panel`_.

A GitHub repository is also required as the deployment source. Depending on
who manages the deployment, use either the original Vocabio repository or a
fork owned by the deployer.

The deployed repository must contain the deployment-ready application,
including:

* ``Dockerfile`` and ``.dockerignore``;
* ``poetry.lock`` and ``pyproject.toml``;
* Gunicorn as a runtime dependency;
* WhiteNoise static-file configuration;
* production-safe Django security settings.

The Neon project, ``vocabiodb`` database, ``vocabio_owner`` role, and pooled
and direct connection strings should be prepared before the first
deployment. See :doc:`neon`.

Choose the deployment repository
--------------------------------

Koyeb deploys Vocabio from a GitHub repository.

If you own the original Vocabio repository, it can be used directly as the
deployment source. Otherwise, fork the repository into your GitHub account
and use that fork for the deployment.

An independent deployment should use Koyeb and Neon resources controlled by
its deployer, together with its own Secrets and Django production
credentials.

A fork is maintained independently from the original repository. Synchronise
upstream changes into the fork before deploying them.

Review the Free Instance
------------------------

Koyeb provides one Free Instance per organisation for a Web Service.

The Free Instance currently provides:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Resource
     - Allowance
   * - Price
     - ``$0``
   * - Memory
     - 512 MB RAM
   * - CPU
     - 0.1 vCPU
   * - Local SSD
     - 2 GB
   * - Free Instances
     - One per organisation
   * - Regions
     - Frankfurt or Washington, D.C.
   * - Scale to zero
     - After one hour without traffic

The Free Instance is sufficient for the current low-traffic personal
Vocabio deployment. Koyeb describes Free Instances as suitable for testing
and hobby projects and does not recommend them for production-grade
applications.

The deployed Vocabio environment still uses production Django settings even
when it runs on the Free Instance.

Access to the Free Instance depends on the organisation's current plan and
account eligibility. Koyeb can change signup and plan requirements, so
review the current pricing and account documentation before creating a new
organisation.

Connect the deployment repository
---------------------------------

Open the `Koyeb control panel`_.

If the Vocabio Web Service does not exist:

#. select ``Create Web Service`` from the Overview page;
#. choose ``GitHub`` as the deployment method;
#. install or configure the Koyeb GitHub App if prompted;
#. grant Koyeb access to the deployment repository;
#. select that repository;
#. select the ``main`` branch.

GitHub authorisation is required only when Koyeb does not already have
access to the repository.

Grant access only to the deployment repository unless broader repository
access is intentionally required.

For repositories connected through the Koyeb GitHub integration,
autodeploy can redeploy the Service when the tracked branch changes. Keep
the setting enabled when pushes to ``main`` should deploy automatically.

Create or configure the Vocabio Web Service
-------------------------------------------

After selecting the deployment repository, review the Service
configuration.

Use:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Setting
     - Value
   * - Service type
     - Web Service
   * - Source branch
     - ``main``
   * - Work directory
     - Repository root
   * - Builder
     - Dockerfile
   * - Dockerfile
     - ``Dockerfile``
   * - Region
     - Frankfurt
   * - Instance type
     - Free
   * - Entrypoint override
     - Disabled
   * - Command override
     - Disabled

Frankfurt is used for this deployment so that the application runs close to
the Neon database configured in the Frankfurt AWS region.

The Free Instance is limited to a single region. If the deployment later
moves to a paid Instance, review the available regions and capacity before
changing the Service configuration.

Configure the Dockerfile build
------------------------------

Koyeb builds Vocabio from the repository root ``Dockerfile``.

The Dockerfile defines the Python runtime, installs Poetry 2.4.1 in a builder
stage, installs the locked production dependencies, collects Django static
files, and creates the final runtime image.

The final runtime image does not contain Poetry.

The production build process is defined entirely by the repository
``Dockerfile``.

The container build is documented in :doc:`docker`.

Static files
------------

The production Dockerfile collects Django static files during the builder
stage.

The build runs:

.. code-block:: console

   python manage.py collectstatic --noinput

Collected files are written to:

.. code-block:: text

   staticfiles/

The Docker build uses non-sensitive build-only Django settings for this step.
Production Koyeb Secrets and the Neon database connection are not required to
collect static files.

The generated directory is copied into the final runtime image and remains
excluded from version control.

WhiteNoise serves the collected files from the running Django application.

Configure the runtime process
-----------------------------

The production web process is defined by the Dockerfile ``CMD``.

The image starts Gunicorn and binds it to the port provided through the
``PORT`` environment variable, falling back to port ``8000`` when the
variable is unavailable.

Koyeb Web Services provide ``PORT`` automatically. When it is not explicitly
configured, Koyeb sets it to the lowest exposed port.

Leave the Koyeb entrypoint and command overrides disabled so that the runtime
process remains defined by the Docker image.

Forwarded client addresses
--------------------------

Koyeb sets the ``X-Forwarded-For`` header and appends the address used to
connect to Koyeb to the end of the forwarded-address chain. Koyeb guarantees
only the final address in that chain as valid.

Vocabio therefore configures ``django-ipware`` to prefer
``HTTP_X_FORWARDED_FOR`` over ``REMOTE_ADDR`` and to resolve the
rightmost forwarded address. This address is used by ``django-axes`` as
part of the login lockout key.

The client IP configuration is security-sensitive. If Vocabio is moved
to a different hosting or reverse-proxy environment, the
forwarded-address policy must be reviewed before deployment.

Store production Secrets
------------------------

Sensitive production values are stored as Koyeb Secrets.

Koyeb Secrets are global to the organisation and encrypted by Koyeb. Access
must be granted to the Service that uses them.

Create Secrets from the ``Secrets`` page in the Koyeb control panel.

The deployment requires separate secret values for:

* the Django production secret key;
* the pooled Neon database connection string;
* the direct Neon database connection string.

Generate a separate Django secret key for the hosted environment with
Django's secret-key generator:

.. code-block:: console

   poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Store the generated value directly as a Koyeb Secret. Do not reuse the
local development secret key.

The exact Secret names are deployment configuration and do not affect the
Django settings contract.

The pooled Neon Secret is exposed to the running Web Service through
``DATABASE_URL``.

The direct Neon Secret is also exposed to the Service through
``DIRECT_DATABASE_URL``. Django does not use this variable for its normal
database configuration; it is reserved for migrations, dumps, restores, and
other controlled database operations.

Database connection preparation and the pooled/direct distinction are
documented in :doc:`neon`.

Configure environment variables
-------------------------------

Open the Service configuration and expand ``Environment variables and
files``.

Environment variable values can be entered individually or through
``Bulk Edit``.

Koyeb supports Secret interpolation with:

.. code-block:: text

   {{ secret.<SECRET_NAME> }}

It also provides deployment-specific variables such as
``KOYEB_PUBLIC_DOMAIN``.

Configure the Vocabio Web Service with:

.. code-block:: text

   DJANGO_SECRET_KEY={{ secret.<django-secret> }}

   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS={{ KOYEB_PUBLIC_DOMAIN }}
   DJANGO_CSRF_TRUSTED_ORIGINS=https://{{ KOYEB_PUBLIC_DOMAIN }}

   DJANGO_SECURE_SSL_REDIRECT=True
   DJANGO_SESSION_COOKIE_SECURE=True
   DJANGO_CSRF_COOKIE_SECURE=True

   DJANGO_SECURE_HSTS_SECONDS=0
   DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
   DJANGO_SECURE_HSTS_PRELOAD=False

   DATABASE_URL={{ secret.<pooled-database-url> }}
   DIRECT_DATABASE_URL={{ secret.<direct-database-url> }}

   DATABASE_CONN_MAX_AGE=30
   DATABASE_CONN_HEALTH_CHECKS=True
   DATABASE_CONNECT_TIMEOUT=5

   DJANGO_LANGUAGE_CODE=en-gb
   DJANGO_TIME_ZONE=UTC

Replace the placeholder Secret references with the actual Koyeb Secret
names configured for the organisation.

``DIRECT_DATABASE_URL`` is available to controlled administrative commands,
but the normal Django web process continues to use only ``DATABASE_URL`` for
its configured database connection.

``KOYEB_PUBLIC_DOMAIN`` is provided automatically for public Web Services.
The resulting value is used both as the allowed Django host and as the HTTPS
CSRF trusted origin.

The HTTP health check must use the same public hostname in its ``Host``
header so that the probe satisfies Django's ``ALLOWED_HOSTS`` validation.

The Django environment variables used by the application are documented in
:doc:`../configuration/environment`.

HTTPS and HSTS
--------------

Koyeb terminates public HTTPS traffic before forwarding requests to the
application.

The Django configuration trusts the forwarded HTTPS protocol header and
uses secure session and CSRF cookies when ``DJANGO_DEBUG`` is ``False``.

The current deployment enables HTTPS redirection:

.. code-block:: text

   DJANGO_SECURE_SSL_REDIRECT=True

HSTS remains disabled initially:

.. code-block:: text

   DJANGO_SECURE_HSTS_SECONDS=0
   DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
   DJANGO_SECURE_HSTS_PRELOAD=False

Keeping HSTS disabled during the initial deployment avoids persisting an
HSTS policy in browsers before the HTTPS and proxy configuration has been
verified.

Enable HSTS only after the deployed HTTPS behaviour has been tested and the
long-term domain configuration is stable.

Configure ports and routing
---------------------------

Configure one public HTTP port:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Setting
     - Value
   * - Port
     - ``8000``
   * - Protocol
     - HTTP
   * - Public route
     - ``/``

Koyeb automatically sets ``PORT`` to the lowest exposed port when it is not
defined explicitly. The Dockerfile runtime command reads this value at runtime.

Do not define a separate ``PORT`` environment variable.

Configure the exposed application port to use an HTTP health check with the
following values:

.. code-block:: text

  Protocol: HTTP
  Method: GET
  Path: /health/live/
  Headers:
    Host: <public-koyeb-domain>
    X-Forwarded-Proto: https

Replace ``<public-koyeb-domain>`` with the actual public Koyeb hostname used
by the deployed Service, without ``https://`` or a trailing slash.

The explicit ``Host`` header is required because Django validates incoming
hostnames against ``DJANGO_ALLOWED_HOSTS``. Without the public Koyeb hostname
in the health-check request, Django can reject the probe with an
``Invalid HTTP_HOST header`` error and the Instance will fail its health
check.

The health check also sends ``X-Forwarded-Proto: https``. Vocabio trusts
this header through ``SECURE_PROXY_SSL_HEADER`` so that Django treats the
probe as secure and executes the liveness view instead of redirecting the
request through ``SECURE_SSL_REDIRECT``.

Without this header, Django can return an HTTPS redirect before the
``/health/live/`` view is reached. Koyeb accepts ``3xx`` responses as healthy,
so the probe could otherwise pass without actually exercising the
application liveness endpoint.

The liveness endpoint verifies that the Django application process can
respond without depending on PostgreSQL availability. Koyeb uses this health
check during Deployment startup and to identify unresponsive Instances.

The separate ``/health/ready/`` endpoint verifies database connectivity and
is available for readiness diagnostics without making temporary external
database failures trigger application restarts.

The public route should forward the application root path to the exposed
HTTP port.

Deploy the Service
------------------

After reviewing the source, builder, Instance, Secrets, environment
variables, ports, and routing, select ``Deploy``.

Koyeb then:

#. clones the configured GitHub revision;
#. reads the repository Dockerfile;
#. builds the Docker image;
#. installs Poetry 2.4.1 in the builder stage;
#. installs the locked runtime dependencies;
#. runs Django static-file collection;
#. creates the final runtime image;
#. starts the Gunicorn process defined by the Dockerfile.

Follow the deployment stages and build logs from the Service page.

A successful build should show the Docker build stages, Poetry 2.4.1
installation, dependency installation, static-file collection, and final
runtime image creation.

Apply database operations separately
------------------------------------

Database migrations are not part of the ``Dockerfile`` and should not run
automatically whenever Gunicorn starts.

Production migrations are controlled operations and must use the direct
Neon connection exposed as ``DIRECT_DATABASE_URL``.

The normal Web Service continues to use the pooled connection exposed as
``DATABASE_URL``.

Do not add ``migrate`` or ``createsuperuser`` to Dockerfile build steps, the
Dockerfile runtime command, or Koyeb command overrides.

Verify the deployment
---------------------

After the first successful deployment and initial database setup, confirm
that:

* the Dockerfile build completes without errors;
* the expected Python 3.13 container base is used;
* Poetry 2.4.1 installs successfully in the builder stage;
* production dependencies install successfully from ``poetry.lock``;
* ``collectstatic`` runs successfully during the image build;
* the final runtime image is created;
* Gunicorn starts successfully from the Dockerfile runtime command;
* the application is reachable through the ``.koyeb.app`` HTTPS URL;
* the Koyeb HTTP health check for ``/health/live/`` passes with the public
  Koyeb hostname supplied as the ``Host`` header and
  ``X-Forwarded-Proto: https`` supplied as the forwarded protocol header;
* HTTPS redirection does not create a redirect loop;
* Django static files are served correctly;
* the pooled Neon database connection is available as ``DATABASE_URL``;
* the direct Neon connection is available as ``DIRECT_DATABASE_URL``;
* production migrations have been applied with the direct connection;
* the Django administration page is available at ``/admin/``.

The public application root at ``/`` should return HTTP 200 from the Vocabio
home route.

The application health endpoints should also be available:

* ``/health/live/`` returns HTTP 200 when the application process is running;
* ``/health/ready/`` returns HTTP 200 when the application can access
  PostgreSQL.

Automatic redeployment
----------------------

Koyeb can automatically redeploy a Service when changes are pushed or
merged into the configured branch of the deployment repository.

For the current deployment, the tracked branch is:

.. code-block:: text

   main

When autodeploy is enabled, a successful deployment replaces the previously
active deployment.

Review build and runtime logs after deployment changes, especially when
dependencies, environment variables, Django settings, or database
configuration have changed.

Operational notes
-----------------

The Free Instance scales to zero after one hour without incoming traffic.
The first request after an idle period can therefore take longer while the
Instance starts again.

Neon can also suspend its compute after database inactivity. A request made
after both services have been idle can therefore experience both the Koyeb
Instance start and the Neon database wake-up.

Monitor Koyeb usage, deployment logs, runtime logs, and Neon resource usage
when diagnosing slow first requests.

Do not store production Secret values in the repository, ``.env.example``,
documentation, issue trackers, logs, or screenshots.

Official references
-------------------

The following official pages provide the current platform documentation:

* `Koyeb documentation`_
* `Deploy with GitHub`_
* `Build from Git`_
* `Environment variables`_
* `Koyeb Secrets`_
* `Koyeb Instances`_
* `Koyeb pricing FAQ`_
* `Koyeb organisations`_
* `Koyeb Services`_
* `Koyeb regions`_
* `Koyeb scale to zero`_
* `Exposing your Service`_
* `Health checks`_
* `Use Neon with Koyeb`_

.. _Koyeb control panel: https://app.koyeb.com/
.. _Koyeb documentation: https://www.koyeb.com/docs
.. _Deploy with GitHub:
   https://www.koyeb.com/docs/build-and-deploy/deploy-with-git
.. _Build from Git:
   https://www.koyeb.com/docs/build-and-deploy/build-from-git
.. _Environment variables:
   https://www.koyeb.com/docs/build-and-deploy/environment-variables
.. _Koyeb Secrets: https://www.koyeb.com/docs/reference/secrets
.. _Koyeb Instances: https://www.koyeb.com/docs/reference/instances
.. _Koyeb pricing FAQ: https://www.koyeb.com/docs/faqs/pricing
.. _Koyeb organisations: https://www.koyeb.com/docs/reference/organizations
.. _Koyeb Services: https://www.koyeb.com/docs/reference/services
.. _Koyeb regions: https://www.koyeb.com/docs/reference/regions
.. _Koyeb scale to zero:
   https://www.koyeb.com/docs/run-and-scale/scale-to-zero
.. _Use Neon with Koyeb: https://neon.com/docs/guides/koyeb
.. _Exposing your Service:
   https://www.koyeb.com/docs/build-and-deploy/exposing-your-service
.. _Health checks:
   https://www.koyeb.com/docs/run-and-scale/health-checks

.. note::

   Koyeb can change Console labels, plan rules, pricing, and service
   behaviour. If the interface differs from this procedure, check the
   official documentation linked above before proceeding.
