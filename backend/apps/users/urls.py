from django.urls import path
from .views.auth import login, refresh, logout, verify_email,register,UserListView,UserDetailView
from apps.users.views.me import me

urlpatterns = [
    path("register/",register),
    path("login/", login),
    path("refresh/", refresh),
    path("logout/", logout),
    path("verify-email/", verify_email, name="verify-email"),
    path("", UserListView.as_view(), name="user-list"),
    path("<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("me/", me, name="me"),
]
