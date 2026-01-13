

from django.contrib.auth import authenticate
from rest_framework.decorators import api_view,authentication_classes
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.services.tokens import rotate_refresh_token
from apps.users.services.tokens import issue_tokens
from apps.users.models import UserSession
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from apps.users.serializers.auth import (
    RegisterSerializer,
    VerifyEmailSerializer,
    LoginSerializer,
    RefreshSerializer,
    LogoutSerializer,
    UserDetailSerializer
)
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from apps.users.models import User

from rest_framework.exceptions import ValidationError

import random
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone




User = get_user_model()

@extend_schema(
    request=RegisterSerializer,
    auth=None,
    responses={200: None},
)
@authentication_classes([]) 
@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    role = request.data.get("role")
    
    valid_roles = [choice[0] for choice in User.Role.choices]

    if role not in valid_roles:
        raise ValidationError(
            f"Invalid role. Choose from {valid_roles}"
        )

    if not all([username, email, password, role]):
        raise ValidationError("All fields are required")

    if User.objects.filter(username=username).exists():
        raise ValidationError("Username already exists")

    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already exists")

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
        is_email_verified=False  
    )

    return Response({
        "message": "User registered successfully. Please verify email."
    })


@extend_schema(
    request=VerifyEmailSerializer,
    auth=None
    )
@authentication_classes([]) 
@api_view(["POST"])
def verify_email(request):
    serializer = VerifyEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = request.data.get("email")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError("Invalid email")

    user.is_email_verified = True
    user.save()

    return Response({"message": "Email verified successfully"})


@extend_schema(request=LoginSerializer,auth=None)
@authentication_classes([]) 
@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = request.data.get("username")
    password = request.data.get("password")
    device = request.data.get("device", "unknown")
    ip = request.META.get("REMOTE_ADDR")

    user = authenticate(username=username, password=password)
   
    if not user:
        register_login_failure(ip)
        raise AuthenticationFailed("Invalid credentials")

    if not user.is_email_verified:
        raise AuthenticationFailed("Email not verified")


    # SUCCESS → reset failures
    cache.delete(f"failures:{ip}")

    tokens = issue_tokens(user, request.data.get("device", "unknown"))
    return Response(tokens)


@extend_schema(request=LogoutSerializer)
@api_view(["POST"])
def logout(request):
    serializer = LogoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    refresh_token = request.data.get("refresh")

    token = RefreshToken(refresh_token)

    UserSession.objects.filter(
        refresh_jti=token["jti"]
    ).delete()

    token.blacklist()

    return Response({"detail": "Logged out successfully"})


@extend_schema(request=RefreshSerializer)
@api_view(["POST"])
def refresh(request):
    serializer = RefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    refresh_token = serializer.validated_data["refresh"]
    device = serializer.validated_data["device"]

    if not refresh_token:
        raise AuthenticationFailed("Refresh token is required")

    try:
        old_refresh = RefreshToken(refresh_token)
    except Exception:
        raise AuthenticationFailed("Invalid refresh token")

    user_id = old_refresh["user_id"]

    
    if not UserSession.objects.filter(refresh_jti=old_refresh["jti"]).exists():
        raise AuthenticationFailed("Session expired or invalid")

    
    new_refresh = rotate_refresh_token(old_refresh, user_id, device)

    return Response({
        "access": str(new_refresh.access_token),
        "refresh": str(new_refresh)
    })


class UserDetailView(RetrieveAPIView):
    """
    GET /users/{id}/
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

def block_ip(ip):
        a = random.randint(1, 9)
        b = random.randint(1, 9)

        cache.set(
            f"blocked:{ip}",
            {
                "question": f"What is {a} + {b}?",
                "answer": a + b,
            },
            timeout=settings.SMART_SECURITY["BLOCK_DURATION_MINUTES"] * 60
        )

def register_login_failure(ip):
    failure_key = f"failures:{ip}"
    failures = cache.get(failure_key, [])

    now = timezone.now()
    failures = [
        ts for ts in failures
        if now - ts < timedelta(minutes=settings.SMART_SECURITY["FAILURE_WINDOW_MINUTES"])
    ]

    failures.append(now)
    cache.set(
        failure_key,
        failures,
        timeout=settings.SMART_SECURITY["FAILURE_WINDOW_MINUTES"] * 60
    )

    if len(failures) > settings.SMART_SECURITY["MAX_FAILURES"]:
        block_ip(ip)

    
