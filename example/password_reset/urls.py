from django.urls import path

from . views import password_commit, password_reset

app_name = "password_reset"

urlpatterns = [
    path("password/reset", password_reset, name="password_reset_form"),
    path("password/commit", password_commit, name="password_commit")
]
