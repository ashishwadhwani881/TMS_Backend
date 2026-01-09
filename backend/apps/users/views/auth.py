from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.services.tokens import rotate_refresh_token
from apps.users.services.tokens import issue_tokens
from apps.users.models import UserSession
from django.contrib.auth import get_user_model


from rest_framework.exceptions import ValidationError

User = get_user_model()

@api_view(["POST"])
def register(request):
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


@api_view(["POST"])
def verify_email(request):
    email = request.data.get("email")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError("Invalid email")

    user.is_email_verified = True
    user.save()

    return Response({"message": "Email verified successfully"})


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    device = request.data.get("device", "unknown")

    user = authenticate(username=username, password=password)
    if not user:
        raise AuthenticationFailed("Invalid credentials")

    if not user.is_email_verified:
        raise AuthenticationFailed("Email not verified")

    tokens = issue_tokens(user, device)
    return Response(tokens)


@api_view(["POST"])
def logout(request):
    refresh_token = request.data.get("refresh")

    token = RefreshToken(refresh_token)

    UserSession.objects.filter(
        refresh_jti=token["jti"]
    ).delete()

    token.blacklist()

    return Response({"detail": "Logged out successfully"})


@api_view(["POST"])
def refresh(request):
    refresh_token = request.data.get("refresh")
    device = request.data.get("device", "unknown")

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