Authentication and access control
=================================

Vocabio uses Django's built-in authentication system and the standard
``django.contrib.auth.User`` model. The project does not define a custom user
model.

The ``accounts`` application provides the Vocabio-specific authentication
interface while relying on Django's standard authentication backend and
session framework.

Authentication routes
---------------------

The application defines the following authentication routes:

.. code-block:: text

   /login/
   /logout/

The routes are namespaced as:

.. code-block:: text

   accounts:login
   accounts:logout

``/login/`` accepts ``GET`` and ``POST`` requests. A ``GET`` request renders
the login form, while a valid ``POST`` request authenticates the user and
creates the Django session.

``/logout/`` accepts ``POST`` requests only. A ``GET`` request is rejected
with HTTP 405 Method Not Allowed.

The Django administration site remains available separately under:

.. code-block:: text

   /admin/

Access to Django Admin is controlled by Django's standard staff and
superuser flags.

Authentication settings
-----------------------

Project-level authentication routing is configured in ``config/settings.py``:

.. code-block:: python

   LOGIN_URL = "accounts:login"
   LOGIN_REDIRECT_URL = "core:home"
   LOGOUT_REDIRECT_URL = "core:home"

``LOGIN_URL`` allows Django authentication and permission helpers to redirect
anonymous users to the Vocabio login route.

After successful authentication, Vocabio redirects to a validated local
``next`` target when one is supplied. Otherwise, the named ``core:home``
route is used.

Successful logout also redirects to ``core:home`` after the authenticated
session has been terminated.

Client IP resolution
--------------------

Vocabio defines a project-wide client IP resolution policy in
``config/settings.py``.

Forwarded addresses are preferred over ``REMOTE_ADDR``, and the right-most
forwarded address is selected for the current Koyeb proxy environment.

The same policy is reused by ``django-axes`` so that application-level
request handling and authentication lockout behaviour resolve client
addresses consistently.

Application code accesses the resolved client address through
``infrastructure.request.get_client_ip`` rather than parsing proxy headers
directly.

Login form
----------

``accounts.forms.LoginForm`` subclasses Django's
``AuthenticationForm`` rather than implementing credential validation
independently.

The form uses the standard username and password authentication fields and
adds browser credential metadata appropriate for an existing account:

.. code-block:: text

   username autocomplete: username
   password autocomplete: current-password

The username field receives autofocus when the login page is opened.

Login behaviour
---------------

Successful authentication creates the normal Django session.

Successful authentication also emits an ``[AUTH|LOGIN]`` audit event with
the authenticated user ID and resolved client IP address.

When a safe ``next`` value is supplied, successful authentication redirects
the user to that local target. Without a valid ``next`` target, the
configured ``LOGIN_REDIRECT_URL`` is used.

Redirect targets supplied through ``next`` are validated before use.
External redirect targets are rejected and fall back to the configured
login redirect.

Invalid credentials do not create an authenticated session. Inactive users
are also prevented from authenticating through the login form.

An already authenticated user who opens the login route is redirected to
``LOGIN_REDIRECT_URL`` rather than being shown the login form again.

Logout behaviour
----------------

Logout is a state-changing operation and therefore accepts ``POST`` only.

Logout also requires an authenticated user. Anonymous POST requests are
redirected to the configured login route without producing an
``[AUTH|LOGOUT]`` audit event.

A successful logout terminates the authenticated Django session and
redirects the user to ``LOGOUT_REDIRECT_URL``.

Before the session is terminated, Vocabio captures the authenticated user ID
and resolved client IP address. Successful logout then emits an
``[AUTH|LOGOUT]`` audit event containing those values.

Security
--------

The authentication flow uses Django's existing security mechanisms rather
than implementing credential handling independently.

The current authentication security properties include:

* CSRF protection for authentication POST requests;
* a CSRF token in the login form;
* authenticated POST-only logout;
* prevention of caching for authentication responses;
* sensitive handling of submitted password data in Django error reports;
* structured audit logging for successful login, logout, and lockout events;
* Django's standard password authentication;
* rejection of unsafe external ``next`` redirect targets;
* inactive-user rejection;
* password input metadata suitable for browser password managers.

The project uses Django's standard
``AuthenticationMiddleware`` to expose the current user through
``request.user``.

No custom application-access middleware is used.

Login attempt protection
------------------------

Vocabio uses ``django-axes`` to protect authentication endpoints against
repeated failed login attempts.

Axes is integrated through ``AxesStandaloneBackend`` and
``AxesMiddleware``. Django's standard ``ModelBackend`` remains responsible
for credential authentication and permission handling.

The current lockout policy is:

* three failed authentication attempts trigger a lockout;
* the third failed attempt is rejected with HTTP 429 Too Many Requests;
* the lockout lasts for 15 minutes;
* failed attempts during a lockout do not extend its duration;
* successful authentication resets accumulated failed attempts;
* lockouts are scoped to the combination of username and IP address;
* the same lockout policy protects both the Vocabio login view and Django
  Admin.

Axes delegates lockout-response handling to
``accounts.security.login_lockout_response``. The callable records an
``[AUTH|LOCKOUT]`` audit event and returns the configured HTTP lockout
response without taking ownership of the lockout decision itself.

The lockout event records the attempted username, resolved client IP
address, and request path. Individual failed attempts remain tracked by
``django-axes`` and are not duplicated as application audit events.

Client IP addresses are resolved through ``django-ipware``.
``HTTP_X_FORWARDED_FOR`` is preferred, with ``REMOTE_ADDR`` used as a
fallback. Forwarded addresses are resolved using the rightmost address so
that production behaviour matches the Koyeb proxy configuration.

Authorisation policy
--------------------

Vocabio separates authentication from authorisation.

The application-level policy is:

* public read-only application views may be accessed without authentication;
* authentication alone does not grant permission to modify application data;
* create, change, and delete operations must be protected by the appropriate
  Django permissions;
* domain-specific permissions belong to the Django application that owns the
  corresponding models;
* superusers have Django's standard full permission set and may also access
  Django Admin.

The ``accounts`` application therefore handles authentication but does not
define a global application-access permission.

Related documentation
---------------------

See also:

* :doc:`structure`
* :doc:`logging`
* :doc:`../development/testing`
* :doc:`../configuration/environment`
