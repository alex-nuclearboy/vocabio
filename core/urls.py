"""URL configuration for the core application."""

from django.urls import path

from core.views.health import liveness, readiness
from core.views.home import home

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("health/live/", liveness, name="health-live"),
    path("health/ready/", readiness, name="health-ready"),
]
