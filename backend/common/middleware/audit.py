from apps.audits.models import AuditLog
from rest_framework_simplejwt.authentication import JWTAuthentication


class AuditLoggingMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):

        response = self.get_response(request)

       
        if request.path.startswith("/api/tasks/analytics/"):
            return response

        user = None
        try:
            auth = self.jwt_auth.authenticate(request)
            if auth:
                user, _ = auth
        except Exception:
            pass

        AuditLog.objects.create(
            user=user,
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        return response
