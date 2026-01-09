from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

class AutoRefreshTokenMiddleware:
    """
    Automatically issues a new access token
    if current token expires within 2 minutes
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        token = getattr(request, "jwt_token", None)
        if not token:
            return response

        exp_timestamp = token["exp"]
        exp_time = timezone.datetime.fromtimestamp(
            exp_timestamp, tz=timezone.utc
        )

        remaining = exp_time - timezone.now()

        if remaining <= timedelta(minutes=2):
            new_token = AccessToken.for_user(request.user)
            response["X-New-Access-Token"] = str(new_token)

        return response
