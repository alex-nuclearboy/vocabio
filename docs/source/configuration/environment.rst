Environment configuration
=========================

Vocabio reads environment-specific and sensitive configuration from
environment variables.

A local ``.env`` file is supported for development. Environment variables
already present in the process environment take precedence over values from
the local file.

The procedure for creating and preparing ``.env`` is documented in
:doc:`../getting-started/local-development`.

Local environment file
----------------------

The repository provides ``.env.example`` as the template for local
configuration. It contains safe local defaults and empty placeholders for
values that must be supplied locally.

The local ``.env`` file must not be committed to the repository. Secret
values must also not be added to ``.env.example``.

Django variables
----------------

``DJANGO_SECRET_KEY``
~~~~~~~~~~~~~~~~~~~~~

Required.

Contains the Django cryptographic signing key. The value must not be empty.

Generate a separate value for local development as described in
:doc:`../getting-started/local-development`.

``DJANGO_DEBUG``
~~~~~~~~~~~~~~~~

Optional.

Controls Django debug mode. The application default is ``False``. The local
``.env.example`` value is ``True``.

Debug mode should be enabled only in a development environment. When it is
``False``, production security validation is applied.

``DJANGO_ALLOWED_HOSTS``
~~~~~~~~~~~~~~~~~~~~~~~~

Required in production.

Contains a comma-separated list of hostnames or IP addresses accepted by
Django. The application default is an empty list.

The local ``.env.example`` value is:

.. code-block:: text

   localhost,127.0.0.1,[::1]

The list allows requests addressed to the local machine using the hostname
``localhost``, the IPv4 loopback address ``127.0.0.1``, or the IPv6 loopback
address ``::1``.

Values must contain hostnames or IP addresses only, without URL schemes,
paths, or trailing slashes.

Surrounding whitespace is removed from individual values when the
configuration is loaded.

When ``DJANGO_DEBUG`` is ``False``, the list must not be empty and must not
contain the wildcard value ``*``.

``DJANGO_CSRF_TRUSTED_ORIGINS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional.

Contains a comma-separated list of trusted origins for unsafe requests such
as ``POST`` requests protected by Django's CSRF validation.

Origins must include the URL scheme. Surrounding whitespace and trailing
slashes are removed when the configuration is loaded.

The local ``.env.example`` value is empty because normal local development
does not require additional trusted origins.

``DJANGO_SECURE_SSL_REDIRECT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional during local development and required to be ``True`` in production.

Controls whether Django redirects HTTP requests to HTTPS. The default value
is ``False``.

The local ``.env.example`` value is also ``False`` because the development
server normally uses HTTP.

When ``DJANGO_DEBUG`` is ``False``, this setting must be ``True``. Otherwise,
the application raises a configuration error during startup.

Production deployment therefore requires working HTTPS and reverse-proxy
handling before the application is started.

The project is configured to recognise HTTPS requests forwarded by a trusted
reverse proxy through the ``X-Forwarded-Proto`` header.

``DJANGO_SESSION_COOKIE_SECURE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional during local development and required to be ``True`` in production.

Controls whether the session cookie is transmitted only over HTTPS. The
default value is ``False``.

The local ``.env.example`` value is ``False``.

When ``DJANGO_DEBUG`` is ``False``, this setting must be ``True``. Otherwise,
the application raises a configuration error during startup.

``DJANGO_CSRF_COOKIE_SECURE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional during local development and required to be ``True`` in production.

Controls whether the CSRF cookie is transmitted only over HTTPS. The default
value is ``False``.

The local ``.env.example`` value is ``False``.

When ``DJANGO_DEBUG`` is ``False``, this setting must be ``True``. Otherwise,
the application raises a configuration error during startup.

``DJANGO_SECURE_HSTS_SECONDS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional.

Defines the HTTP Strict Transport Security duration in seconds. The default
value is ``0``, which disables HSTS.

Negative values are rejected.

The local ``.env.example`` value is ``0``. HSTS should remain disabled until
HTTPS behaviour has been verified in the deployment environment.

``DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional.

Controls whether the HSTS policy also applies to subdomains. The default
value is ``False``.

The local ``.env.example`` value is also ``False``.

``DJANGO_SECURE_HSTS_PRELOAD``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional.

Controls whether Django adds the HSTS preload directive to the
``Strict-Transport-Security`` header. The default value is ``False``.

The local ``.env.example`` value is also ``False``.

Local PostgreSQL variables
--------------------------

The following variables configure the PostgreSQL service started by Docker
Compose. They are used to initialise the container and to construct the local
``DATABASE_URL``.

Docker Compose requires ``POSTGRES_DB``, ``POSTGRES_USER``,
``POSTGRES_PASSWORD``, and ``POSTGRES_PORT`` to be defined before the local
PostgreSQL service can be started. Compose configuration fails immediately
when any of these required values is missing.

``POSTGRES_DB``
~~~~~~~~~~~~~~~

The local database name.

The ``.env.example`` value is:

.. code-block:: text

   vocabio

``POSTGRES_USER``
~~~~~~~~~~~~~~~~~

The local PostgreSQL role.

The ``.env.example`` value is:

.. code-block:: text

   vocabio

``POSTGRES_PASSWORD``
~~~~~~~~~~~~~~~~~~~~~

Required for the local Docker Compose environment.

Contains the password for the local PostgreSQL role. The value is
intentionally empty in ``.env.example``.

Because the same raw value is supplied to PostgreSQL and interpolated into
``DATABASE_URL``, use a sufficiently long password containing letters,
digits, hyphens, and underscores.

``POSTGRES_HOST``
~~~~~~~~~~~~~~~~~

The host used by Django to reach the local PostgreSQL service.

The ``.env.example`` value is:

.. code-block:: text

   127.0.0.1

``POSTGRES_PORT``
~~~~~~~~~~~~~~~~~

The host port published by Docker Compose for PostgreSQL.

The ``.env.example`` value is:

.. code-block:: text

   5432

Change this value if the default PostgreSQL port is already in use locally.

Database connection variables
-----------------------------

``DATABASE_URL``
~~~~~~~~~~~~~~~~

Required.

Defines the PostgreSQL connection used by Django.

The local ``.env.example`` value is assembled from the PostgreSQL variables:

.. code-block:: text

   DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

Environment-variable references are expanded before Django builds the
database configuration.

Detailed URL validation rules are documented in
:doc:`database`.

``DATABASE_CONN_MAX_AGE``
~~~~~~~~~~~~~~~~~~~~~~~~~

Optional.

Defines the maximum lifetime of persistent database connections in seconds.
The default value is ``0``.

A value of ``0`` closes the connection at the end of each request. Negative
values are rejected.

The local ``.env.example`` value is ``0``. The current production Koyeb
configuration uses ``30``.

``DATABASE_CONN_HEALTH_CHECKS``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional.

Controls Django connection health checks. The default value is ``False``.

The local ``.env.example`` value is ``False``. The current production Koyeb
configuration uses ``True``.

``DATABASE_CONNECT_TIMEOUT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional.

Defines the PostgreSQL connection timeout in seconds. The default value is
``5`` and the configured value must be greater than zero.

Application locale and time zone
--------------------------------

``DJANGO_LANGUAGE_CODE``
~~~~~~~~~~~~~~~~~~~~~~~~

Optional.

Defines the Django language code. The configured project default is
``en-gb``.

The local ``.env.example`` value is also:

.. code-block:: text

   en-gb

``DJANGO_TIME_ZONE``
~~~~~~~~~~~~~~~~~~~~

Optional.

Defines the Django time zone. The configured project default is ``UTC``.

The local ``.env.example`` value is also:

.. code-block:: text

   UTC

Use a valid IANA time zone name when changing this value.

Production deployment values
----------------------------

The production Koyeb Service uses the same Django environment-variable
contract with deployment-specific values.

The current production configuration uses:

.. code-block:: text

   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS={{ KOYEB_PUBLIC_DOMAIN }}
   DJANGO_CSRF_TRUSTED_ORIGINS=https://{{ KOYEB_PUBLIC_DOMAIN }}

   DJANGO_SECURE_SSL_REDIRECT=True
   DJANGO_SESSION_COOKIE_SECURE=True
   DJANGO_CSRF_COOKIE_SECURE=True

   DJANGO_SECURE_HSTS_SECONDS=0
   DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=False
   DJANGO_SECURE_HSTS_PRELOAD=False

   DATABASE_CONN_MAX_AGE=30
   DATABASE_CONN_HEALTH_CHECKS=True
   DATABASE_CONNECT_TIMEOUT=5

   DJANGO_LANGUAGE_CODE=en-gb
   DJANGO_TIME_ZONE=UTC

``DJANGO_SECRET_KEY`` and ``DATABASE_URL`` also remain required in
production, but their values are supplied through Koyeb Secrets and must
not be stored in repository documentation.

``DIRECT_DATABASE_URL`` is also present in the Koyeb Service environment,
but it is not read by the Django settings module. It is reserved for
controlled production database operations.

The complete Koyeb Service configuration is documented in
:doc:`../deployment/koyeb`, while production database operations are
documented in :doc:`../deployment/operations`.

Local configuration summary
---------------------------

The local environment currently uses:

.. list-table::
   :header-rows: 1
   :widths: 35 25 40

   * - Variable
     - Local value
     - Status
   * - ``DJANGO_SECRET_KEY``
     - Local secret
     - Required, non-empty
   * - ``DJANGO_DEBUG``
     - ``True``
     - Optional
   * - ``DJANGO_ALLOWED_HOSTS``
     - ``localhost,127.0.0.1,[::1]``
     - Required in production
   * - ``DJANGO_CSRF_TRUSTED_ORIGINS``
     - Empty
     - Optional
   * - ``DJANGO_SECURE_SSL_REDIRECT``
     - ``False``
     - Required as ``True`` in production
   * - ``DJANGO_SESSION_COOKIE_SECURE``
     - ``False``
     - Required as ``True`` in production
   * - ``DJANGO_CSRF_COOKIE_SECURE``
     - ``False``
     - Required as ``True`` in production
   * - ``DJANGO_SECURE_HSTS_SECONDS``
     - ``0``
     - Optional
   * - ``DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS``
     - ``False``
     - Optional
   * - ``DJANGO_SECURE_HSTS_PRELOAD``
     - ``False``
     - Optional
   * - ``POSTGRES_DB``
     - ``vocabio``
     - Required by Docker Compose
   * - ``POSTGRES_USER``
     - ``vocabio``
     - Required by Docker Compose
   * - ``POSTGRES_PASSWORD``
     - Local secret
     - Required by Docker Compose
   * - ``POSTGRES_HOST``
     - ``127.0.0.1``
     - Required by local ``DATABASE_URL``
   * - ``POSTGRES_PORT``
     - ``5432``
     - Required by Docker Compose
   * - ``DATABASE_URL``
     - Local PostgreSQL URL
     - Required
   * - ``DATABASE_CONN_MAX_AGE``
     - ``0``
     - Optional
   * - ``DATABASE_CONN_HEALTH_CHECKS``
     - ``False``
     - Optional
   * - ``DATABASE_CONNECT_TIMEOUT``
     - ``5``
     - Optional
   * - ``DJANGO_LANGUAGE_CODE``
     - ``en-gb``
     - Optional
   * - ``DJANGO_TIME_ZONE``
     - ``UTC``
     - Optional

Applying local changes
----------------------

Restart the Django development server after changing values used by Django.

If ``POSTGRES_PORT`` changes, recreate or update the Compose service so that
the new port mapping is applied:

.. code-block:: console

   docker compose up -d postgres

``POSTGRES_DB``, ``POSTGRES_USER``, and ``POSTGRES_PASSWORD`` are used when
the PostgreSQL data volume is first initialised. Changing them does not
automatically reconfigure an existing database stored in ``postgres_data``.

For database-specific behaviour, see :doc:`database`.
