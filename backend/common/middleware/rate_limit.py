from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse

from rest_framework.authentication import get_authorization_header
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.audits.models import RateLimitCounter
from common.rate_limits import RATE_LIMITS


class RoleBasedRateLimitMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):

       
        try:
            user_auth_tuple = self.jwt_auth.authenticate(request)
        except Exception:
            user_auth_tuple = None

        if user_auth_tuple is None:
            return self.get_response(request)

        user, token = user_auth_tuple

      
        request.user = user

        role = user.role
        method = request.method

        is_read = method in ("GET", "HEAD")
        is_write = not is_read

        limits = RATE_LIMITS.get(role)

        
        if role == "AUDITOR" and is_write:
            return JsonResponse(
                {"detail": "Auditors have read-only access"},
                status=403
            )

        now = timezone.now()
        window_start = now.replace(minute=0, second=0, microsecond=0)

        counter, _ = RateLimitCounter.objects.get_or_create(
            user=user,
            window_start=window_start
        )

        if is_read:
            read_limit = limits["read"]
            if read_limit is not None and counter.read_count >= read_limit:
                return JsonResponse(
                    {"detail": "Read rate limit exceeded"},
                    status=429
                )

        if is_write:
            write_limit = limits["write"]
            if write_limit is not None and counter.write_count >= write_limit:
                seconds_left = int(
                    (window_start + timedelta(hours=1) - now).total_seconds()
                )
                response = JsonResponse(
                    {"detail": "Write rate limit exceeded"},
                    status=429
                )
                response["X-Write-Available-In"] = seconds_left
                return response

        response = self.get_response(request)

        
        if 200 <= response.status_code < 300:
            if is_read:
                counter.read_count += 1
            else:
                counter.write_count += 1
            counter.save(update_fields=["read_count", "write_count"])

        return response
