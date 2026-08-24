"""Tests for the accounts authentication views."""

import pytest
from django.test import Client
from django.urls import reverse

from tests.assertions import assert_response_is_not_cached

pytestmark = pytest.mark.django_db


def test_login_page_is_available(client):
    """Anonymous users can open the login page."""
    response = client.get(
        reverse("accounts:login"),
        secure=True,
    )

    assert response.status_code == 200
    assert "form" in response.context


def test_login_page_renders_authentication_form(client):
    """The login page renders the authentication form securely."""
    response = client.get(
        reverse("accounts:login"),
        secure=True,
    )

    content = response.content.decode()

    assert '<html lang="en-gb">' in content
    assert 'method="post"' in content
    assert f'action="{reverse("accounts:login")}"' in content
    assert 'name="username"' in content
    assert 'autocomplete="username"' in content
    assert "autofocus" in content
    assert 'name="password"' in content
    assert 'type="password"' in content
    assert 'autocomplete="current-password"' in content
    assert 'name="csrfmiddlewaretoken"' in content


def test_login_page_is_not_cached(client):
    """The login page prevents browser and intermediary caching."""
    response = client.get(
        reverse("accounts:login"),
        secure=True,
    )

    assert_response_is_not_cached(response)


def test_login_rejects_post_without_csrf():
    """Login rejects POST requests without a valid CSRF token."""
    csrf_client = Client(enforce_csrf_checks=True)

    response = csrf_client.post(
        reverse("accounts:login"),
        {
            "username": "editor",
            "password": "test-password",
        },
        secure=True,
    )

    assert response.status_code == 403


def test_login_page_preserves_safe_next_url(client):
    """The login page preserves a safe local redirect target."""
    response = client.get(
        reverse("accounts:login"),
        {
            "next": "/words/example/edit/",
        },
        secure=True,
    )

    assert response.status_code == 200
    assert response.context["next"] == "/words/example/edit/"


def test_login_page_renders_safe_next_url(client):
    """The login form includes a safe local redirect target."""
    response = client.get(
        reverse("accounts:login"),
        {
            "next": "/words/example/edit/",
        },
        secure=True,
    )

    content = response.content.decode()

    assert 'name="next"' in content
    assert 'value="/words/example/edit/"' in content


def test_login_page_rejects_external_next_url(client):
    """The login page does not preserve an external redirect target."""
    response = client.get(
        reverse("accounts:login"),
        {
            "next": "https://example.com/",
        },
        secure=True,
    )

    assert response.status_code == 200
    assert response.context["next"] == ""


def test_login_page_does_not_render_external_next_url(client):
    """The login form excludes an unsafe external redirect target."""
    response = client.get(
        reverse("accounts:login"),
        {
            "next": "https://example.com/",
        },
        secure=True,
    )

    content = response.content.decode()

    assert 'name="next"' not in content


def test_empty_login_form_shows_field_errors(client):
    """An empty login submission shows the required field errors."""
    response = client.post(
        reverse("accounts:login"),
        {},
        secure=True,
    )

    form = response.context["form"]

    assert response.status_code == 200
    assert form.errors["username"]
    assert form.errors["password"]
    assert "_auth_user_id" not in client.session


def test_valid_credentials_log_user_in(client, django_user_model):
    """Valid credentials authenticate the user."""
    user = django_user_model.objects.create_user(
        username="editor",
        password="test-password",
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": user.username,
            "password": "test-password",
        },
        secure=True,
    )

    assert response.status_code == 302
    assert response.url == reverse("core:home")
    assert client.session["_auth_user_id"] == str(user.pk)


def test_invalid_credentials_show_login_error(client, django_user_model):
    """Invalid credentials leave the user unauthenticated and show an error."""
    django_user_model.objects.create_user(
        username="editor",
        password="correct-password",
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "editor",
            "password": "wrong-password",
        },
        secure=True,
    )

    form = response.context["form"]
    content = response.content.decode()

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session
    assert form.non_field_errors()
    assert 'role="alert"' in content


def test_inactive_user_cannot_log_in(client, django_user_model):
    """Inactive users cannot authenticate through the login form."""
    django_user_model.objects.create_user(
        username="editor",
        password="test-password",
        is_active=False,
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "editor",
            "password": "test-password",
        },
        secure=True,
    )

    form = response.context["form"]

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session
    assert form.non_field_errors()


def test_authenticated_user_is_redirected_from_login(
    client,
    django_user_model,
):
    """Authenticated users do not see the login form again."""
    user = django_user_model.objects.create_user(
        username="editor",
        password="test-password",
    )
    client.force_login(user)

    response = client.get(
        reverse("accounts:login"),
        secure=True,
    )

    assert response.status_code == 302
    assert response.url == reverse("core:home")


def test_logout_requires_post(client):
    """Logout rejects GET requests."""
    response = client.get(
        reverse("accounts:logout"),
        secure=True,
    )

    assert response.status_code == 405


def test_anonymous_user_cannot_log_out(client):
    """Anonymous users are redirected to login from the logout endpoint."""
    response = client.post(
        reverse("accounts:logout"),
        secure=True,
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:login")


def test_logout_rejects_post_without_csrf(django_user_model):
    """Logout rejects POST requests without a valid CSRF token."""
    user = django_user_model.objects.create_user(
        username="editor",
        password="test-password",
    )

    csrf_client = Client(enforce_csrf_checks=True)
    csrf_client.force_login(user)

    response = csrf_client.post(
        reverse("accounts:logout"),
        secure=True,
    )

    assert response.status_code == 403
    assert "_auth_user_id" in csrf_client.session


def test_logout_ends_authenticated_session(client, django_user_model):
    """A POST request logs out the authenticated user."""
    user = django_user_model.objects.create_user(
        username="editor",
        password="test-password",
    )
    client.force_login(user)

    response = client.post(
        reverse("accounts:logout"),
        secure=True,
    )

    assert response.status_code == 302
    assert response.url == reverse("core:home")
    assert "_auth_user_id" not in client.session


def test_login_redirects_to_safe_next_url(client, django_user_model):
    """Successful login honours a safe local redirect target."""
    django_user_model.objects.create_user(
        username="editor",
        password="test-password",
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "editor",
            "password": "test-password",
            "next": "/words/example/edit/",
        },
        secure=True,
    )

    assert response.status_code == 302
    assert response.url == "/words/example/edit/"


def test_login_rejects_external_next_url(client, django_user_model):
    """Successful login does not redirect to an external host."""
    django_user_model.objects.create_user(
        username="editor",
        password="test-password",
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "editor",
            "password": "test-password",
            "next": "https://example.com/",
        },
        secure=True,
    )

    assert response.status_code == 302
    assert response.url == reverse("core:home")
