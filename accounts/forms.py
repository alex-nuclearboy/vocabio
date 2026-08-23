"""Authentication forms for the accounts application."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    """Authenticate a user with the standard Django authentication system."""

    username = UsernameField(
        label=_("Username"),
        widget=forms.TextInput(
            attrs={
                "autocomplete": "username",
                "autofocus": True,
            },
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
            },
        ),
    )
