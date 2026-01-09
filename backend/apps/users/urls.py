from django.urls import path
from .views.auth import login, refresh, logout, verify_email,register
from apps.users.views.me import me

urlpatterns = [
    path("register/",register),
    path("login/", login),
    path("refresh/", refresh),
    path("logout/", logout),
    path("verify-email/", verify_email, name="verify-email"),
    path("me/", me, name="me"),
]
