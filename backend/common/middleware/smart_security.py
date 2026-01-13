import random
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone


class SmartSecurityMiddleware:
    """
    - Smart CORS
    - IP-based auth failure tracking
    - CAPTCHA challenge on block
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_failures = settings.SMART_SECURITY["MAX_FAILURES"]
        self.failure_window = settings.SMART_SECURITY["FAILURE_WINDOW_MINUTES"]
        self.block_duration = settings.SMART_SECURITY["BLOCK_DURATION_MINUTES"]

    def __call__(self, request):
        ip = self.get_client_ip(request)

       
        origin = request.headers.get("Origin")
        if origin and origin not in settings.ALLOWED_ORIGINS:
            return JsonResponse(
                {"detail": "CORS origin not allowed"},
                status=403
            )

        
        block_key = f"blocked:{ip}"
        block_data = cache.get(block_key)

        if block_data:
            return self.handle_blocked_ip(request, ip, block_data)

        response = self.get_response(request)
        return response

    def handle_blocked_ip(self, request, ip, block_data):
        """
        If IP is blocked, require CAPTCHA
        """
        expected_answer = block_data["answer"]
        provided_answer = request.headers.get("X-Captcha-Answer")

        if provided_answer and provided_answer == str(expected_answer):
            
            cache.delete(f"blocked:{ip}")
            cache.delete(f"failures:{ip}")
            return self.get_response(request)

        
        return JsonResponse(
            {
                "detail": "IP blocked due to multiple failed logins",
                "captcha_question": block_data["question"],
                "retry_after_minutes": self.block_duration,
            },
            status=403,
        )

    def get_client_ip(self, request):
        return request.META.get("REMOTE_ADDR")
