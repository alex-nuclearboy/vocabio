Logging
=======

Overview
--------

Vocabio uses Python and Django logging for runtime diagnostics and a
dedicated audit logger namespace for security-relevant and data-changing
application events.

Logging configuration is built in ``config/logging.py`` and applied through
the Django ``LOGGING`` setting.

Logging environments
--------------------

During local development, log messages are written to both the console and
``logs/vocabio.log``.

Console output uses colours according to log severity:

* ``DEBUG`` — cyan;
* ``INFO`` — green;
* ``WARNING`` — yellow;
* ``ERROR`` — red;
* ``CRITICAL`` — bold red.

The local file uses plain text without terminal colour sequences. It is
rotated at 5 MB and retains three backup files.

Production does not write persistent application log files inside the
container. Log messages are emitted through the console and collected by
the hosting platform.

Log levels
----------

Vocabio uses different logger thresholds according to environment.

Application loggers use ``DEBUG`` during local development and ``INFO`` in
production. Django and django-axes are reduced to ``WARNING`` in production
to avoid unnecessary framework noise.

The root logger uses ``WARNING`` in all environments.

The ``vocabio.audit`` namespace uses ``INFO`` in all environments so that
audit events do not depend on the Django debug setting.

Logger namespaces
-----------------

Regular application code uses module-based logger names such as:

* ``accounts``;
* ``core``;
* ``infrastructure``.

Audit events use the dedicated ``vocabio.audit`` namespace, with
application-specific child loggers such as ``vocabio.audit.accounts`` and
``vocabio.audit.words``.

Audit event convention
----------------------

Audit events use a stable ``[SUBJECT|ACTION]`` identifier followed by
structured ``key=value`` fields.

Examples include:

.. code-block:: text

   [AUTH|LOGIN] user_id=4 client_ip=203.0.113.10
   [AUTH|LOGOUT] user_id=4 client_ip=203.0.113.10
   [AUTH|LOCKOUT] username="editor" client_ip=203.0.113.10 path="/login/"
   [ACCESS|DENIED] user_id=4 client_ip=203.0.113.10

Event subjects use singular names and stable uppercase identifiers.

The event identifier describes what happened, while the logging level
describes its severity. Informational authentication and domain mutation
events use ``INFO``. Lockouts and denied access use ``WARNING``.

Current authentication audit events
-----------------------------------

Vocabio currently emits the following application audit events:

``[AUTH|LOGIN]``
   Records successful authentication with the authenticated user ID and
   resolved client IP address.

``[AUTH|LOGOUT]``
   Records the end of an authenticated application session with the user ID
   and resolved client IP address.

``[AUTH|LOCKOUT]``
   Records an authentication attempt rejected by django-axes lockout
   handling. The event includes the attempted username, resolved client IP
   address, and request path.

Lockout events are emitted when django-axes produces a lockout response,
including requests rejected while an existing lockout remains active.

Individual failed authentication attempts remain tracked by ``django-axes``
and are not duplicated as separate Vocabio audit events.

Sensitive data
--------------

Application and audit logs must never contain:

* passwords;
* session identifiers;
* CSRF tokens;
* secret keys;
* database connection strings;
* authentication cookies;
* complete form submissions or request bodies.

Client IP addresses may be recorded for security and audit purposes.
Application code resolves client addresses through
``infrastructure.request.get_client_ip``.

Audit records should identify persistent domain objects by stable database
identifiers rather than copying complete object contents into log messages.

Retention
---------

Database records maintained internally by ``django-axes`` are separate from
Vocabio application logs.

No automated django-axes retention task is currently configured. Database
log retention will be reviewed separately when operational requirements
justify scheduled maintenance.

Related documentation
---------------------

See also:

* :doc:`authentication`
* :doc:`structure`
* :doc:`../development/testing`
