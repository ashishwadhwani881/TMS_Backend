from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication


class IPWhitelistMiddleware:
   
    ALLOWED_IPS = {
        "127.0.0.1",       
        "10.0.1.152",    
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def __call__(self, request):

        client_ip = request.META.get("REMOTE_ADDR")

        
        user_auth = None
        try:
            user_auth = self.jwt_auth.authenticate(request)
        except Exception:
            pass

        if user_auth:
            user, _ = user_auth

           
            if user.role == "AUDITOR":
                return self.get_response(request)

        
        if client_ip not in self.ALLOWED_IPS:
            return JsonResponse(
                {"detail": "IP not allowed"},
                status=403
            )

        return self.get_response(request)
