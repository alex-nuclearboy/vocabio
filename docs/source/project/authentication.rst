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
   LOGIN_REDIRECT_URL = "/"
   LOGOUT_REDIRECT_URL = "/"

``LOGIN_URL`` allows Django authentication and permission helpers to redirect
anonymous users to the Vocabio login route.

The login and logout redirect settings currently use the public application
root as their default destination.

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

A successful logout terminates the authenticated Django session and
redirects the user to ``LOGOUT_REDIRECT_URL``.

Security
--------

The authentication flow uses Django's existing security mechanisms rather
than implementing credential handling independently.

The current authentication security properties include:

* CSRF protection for authentication POST requests;
* a CSRF token in the login form;
* POST-only logout;
* prevention of caching for authentication responses;
* sensitive handling of submitted password data in Django error reports;
* Django's standard password authentication;
* rejection of unsafe external ``next`` redirect targets;
* inactive-user rejection;
* password input metadata suitable for browser password managers.

The project uses Django's standard
``AuthenticationMiddleware`` to expose the current user through
``request.user``.

No custom application-access middleware is used.

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
* :doc:`../development/testing`
* :doc:`../configuration/environment`
