from dataclasses import fields
from typing import Any

from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from accounts.models import Follow, Profile, User


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


class FollowSerializer(serializers.ModelSerializer):
    follower_username = serializers.CharField(
        source="follower.username", read_only=True
    )
    following_username = serializers.CharField(
        source="following.username", read_only=True
    )

    class Meta:
        model = Follow
        fields = (
            "id",
            "follower",
            "follower_username",
            "following",
            "following_username",
            "created_at",
        )
        read_only_fields = (
            "id",
            "follower",
            "follower_username",
            "following",
            "following_username",
            "created_at",
        )


class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ("avatar", "bio", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")

    def validate_avatar(self, value: UploadedFile) -> UploadedFile:
        max_size = 2 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(detail="Avatar size must be under 2MB")
        valid_types = ["image/jpeg", "image/png", "image/webp"]
        if value.content_type not in valid_types:
            raise serializers.ValidationError(
                detail="Only JPEG, PNG, or WEBP images are allowed."
            )
        return value
