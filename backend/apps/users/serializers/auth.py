from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "role",
            "is_active",
        ]
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.Role.choices)


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    device = serializers.CharField(required=False, default="unknown")


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    device = serializers.CharField(required=False, default="unknown")


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
