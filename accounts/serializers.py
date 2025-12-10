from dataclasses import fields
from typing import Any

from rest_framework import serializers

from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "display_name")

    def create(self, validated_data: dict[str, Any]):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.display_name = validated_data.get("display_name", "")
        user.save()
        return user
