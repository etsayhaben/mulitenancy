from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from tenant_db.models import User

# core/serializers.py
from rest_framework import serializers
from tenant_db.models import User
from .roles import RoleChoices

# core/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["roles"] = [g.name for g in user.groups.all()]
        token["permissions"] = list(user.get_all_permissions())
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["username"] = self.user.username
        data["roles"] = [g.name for g in self.user.groups.all()]
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=RoleChoices.as_choices())

    class Meta:
        model = User
        fields = ["username", "password", "role"]

    def create(self, validated_data):
        # Use create_user to handle password hashing
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            role=validated_data["role"],
        )
        return user
