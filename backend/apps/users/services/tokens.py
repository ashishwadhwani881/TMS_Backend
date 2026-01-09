from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from apps.users.models import UserSession
from django.contrib.auth import get_user_model 

MAX_SESSIONS = 3

User = get_user_model()

def issue_tokens(user, device):
    active_sessions = UserSession.objects.filter(user=user)

    if active_sessions.count() >= MAX_SESSIONS:
        raise AuthenticationFailed("Max device limit reached")

    refresh = RefreshToken.for_user(user)

    UserSession.objects.create(
        user=user,
        refresh_jti=refresh["jti"],
        device=device
    )

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def rotate_refresh_token(old_refresh_token, user_id, device):
    old_jti = old_refresh_token["jti"]

    # Remove old session
    UserSession.objects.filter(refresh_jti=old_jti).delete()

    user = User.objects.get(id=user_id)

    new_refresh = RefreshToken.for_user(user)

    UserSession.objects.create(
        user=user,
        refresh_jti=new_refresh["jti"],
        device=device
    )

    return new_refresh
