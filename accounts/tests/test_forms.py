"""Tests for the accounts authentication forms."""

from accounts.forms import LoginForm


def test_login_form_uses_expected_labels():
    """The login form uses the Vocabio authentication field labels."""
    form = LoginForm()

    assert form.fields["username"].label == "Username"
    assert form.fields["password"].label == "Password"


def test_login_form_configures_username_autocomplete():
    """The username field supports browser credential completion."""
    form = LoginForm()

    assert form.fields["username"].widget.attrs["autocomplete"] == "username"
    assert form.fields["username"].widget.attrs["autofocus"] is True


def test_login_form_configures_password_autocomplete():
    """The password field identifies an existing account password."""
    form = LoginForm()

    assert (
        form.fields["password"].widget.attrs["autocomplete"]
        == "current-password"
    )
