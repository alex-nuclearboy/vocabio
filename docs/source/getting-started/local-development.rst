Local development
=================

This document describes the local environment setup and routine development
workflow for Vocabio.

Complete the :doc:`installation` steps before configuring the local
environment.

The complete environment variable reference is available in
:doc:`../configuration/environment`. Database-specific configuration and
validation rules are documented in
:doc:`../configuration/database`.

Create the local environment file
---------------------------------

Create ``.env`` from ``.env.example`` in the repository root:

.. code-block:: console

   poetry run python -c "from pathlib import Path; source=Path('.env.example'); target=Path('.env'); data=source.read_bytes(); target.touch(exist_ok=False); target.write_bytes(data)"

The command works on Windows, Linux, and macOS. It creates ``.env`` only if
the file does not already exist. If ``.env`` already exists, the command
raises ``FileExistsError`` without changing its contents.

If ``.env.example`` is missing, the command raises ``FileNotFoundError`` and
does not create ``.env``.

The local ``.env`` file contains environment-specific values and must not be
committed to the repository.

Configure required local values
-------------------------------

Open ``.env`` and replace the required empty values.

Django secret key
~~~~~~~~~~~~~~~~~

Generate a Django secret key for local development:

.. code-block:: console

   poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Paste the generated value after the equals sign in:

.. code-block:: text

   DJANGO_SECRET_KEY=

Use a separate key for the local environment. Do not commit the generated
value.

PostgreSQL password
~~~~~~~~~~~~~~~~~~~

Create a password used only by the local PostgreSQL container and paste it
after the equals sign in:

.. code-block:: text

   POSTGRES_PASSWORD=

Use a sufficiently long password containing URL-safe characters (letters,
digits, hyphens, and underscores). The same raw value is supplied to
PostgreSQL and interpolated into ``DATABASE_URL``.

The remaining values in ``.env.example`` can normally keep their local
defaults. See :doc:`../configuration/environment` for the purpose and
default behaviour of each variable.

Validate the Docker Compose configuration
-----------------------------------------

Validate the Compose configuration without printing the resolved values:

.. code-block:: console

   docker compose config --quiet

A successful command produces no output.

Start PostgreSQL
----------------

Start the local PostgreSQL service:

.. code-block:: console

   docker compose up -d postgres

Check the service status:

.. code-block:: console

   docker compose ps

Continue after the ``postgres`` service reports a healthy status.

A PostgreSQL database must be available before running database-dependent
Django commands or tests.

The named ``postgres_data`` Docker volume preserves the local database
between container restarts and routine development sessions.

Initialise the local database
-----------------------------

Apply all committed Django migrations:

.. code-block:: console

   poetry run python manage.py migrate

Run Django system checks:

.. code-block:: console

   poetry run python manage.py check

A successful check completes without reporting configuration errors.

Run the development server
--------------------------

Start the Django development server:

.. code-block:: console

   poetry run python manage.py runserver

Open the application in your browser:

`http://127.0.0.1:8000/ <http://127.0.0.1:8000/>`_

The development server keeps the current terminal occupied while it is
running. Stop it with ``Ctrl+C``.

Routine development workflow
----------------------------

For routine local work, start PostgreSQL:

.. code-block:: console

   docker compose up -d postgres
   docker compose ps

Continue after the service reports a healthy status.

When ``pyproject.toml`` or ``poetry.lock`` has changed, synchronise the Poetry
environment:

.. code-block:: console

   poetry install --with dev

When new committed migrations are available, apply them before running the
application:

.. code-block:: console

   poetry run python manage.py migrate

Start the development server when the application needs to be accessed in a
browser:

.. code-block:: console

   poetry run python manage.py runserver

Stop the server with ``Ctrl+C`` when it is no longer needed.

When local work is finished, stop PostgreSQL without deleting its data:

.. code-block:: console

   docker compose stop postgres

To remove the stopped container and the Compose network while preserving the
database volume, use:

.. code-block:: console

   docker compose down

Do not add ``--volumes`` unless the local database is intentionally being
deleted.

Development checks
------------------

Run the project quality checks before committing substantial changes.

The complete local check sequence is documented in
:doc:`../development/code-quality`. Testing and coverage are described in
:doc:`../development/testing`.

Continuous integration runs the corresponding automated checks as documented
in :doc:`../development/continuous-integration`.

The Django development server does not need to be running for these checks.
PostgreSQL should be running when a command or test requires a database
connection.

Related documentation
---------------------

See also:

* :doc:`../configuration/environment`
* :doc:`../configuration/database`
* :doc:`../development/testing`
* :doc:`../development/code-quality`
* :doc:`../development/continuous-integration`
