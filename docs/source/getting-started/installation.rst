Installation
============

This document describes the one-time preparation of a local Vocabio
development copy.

Before continuing, make sure the software described in
:doc:`requirements` is available.

Clone the repository
--------------------

Clone the repository using the repository URL provided by the Git hosting
service:

.. code-block:: console

   git clone <repository-url>

The URL may use HTTPS or SSH, depending on the authentication method
configured on the local machine.

Open the project directory:

.. code-block:: console

   cd vocabio

Install dependencies
--------------------

Install the application and development dependencies recorded in
``poetry.lock``:

.. code-block:: console

   poetry install --with dev

Poetry creates or reuses an isolated virtual environment for the project.

Verify the environment
----------------------

Confirm which Python interpreter Poetry is using:

.. code-block:: console

   poetry run python --version

The reported version must satisfy the Python requirement in
``pyproject.toml``.

Validate the Poetry project configuration:

.. code-block:: console

   poetry check

A successful command completes without reporting configuration errors.

Next step
---------

After the repository and Python environment are ready, continue with
:doc:`local-development` to configure the local environment, start
PostgreSQL, and run the application.
