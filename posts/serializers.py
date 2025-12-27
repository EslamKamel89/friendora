from typing import Required

from rest_framework import serializers

from posts.models import Post, Tag

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = ("image/jpeg", "image/png", "image/webp")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    tags = serializers.SlugRelatedField(
        read_only=True,
        many=True,
        slug_field="name",
    )
    tags_input = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        allow_empty_file=True,
    )

    def create(self, validated_data):
        tags_data = validated_data.pop("tags_input", [])
        post = Post.objects.create(**validated_data)
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            post.tags.add(tag)
        return post

    def update(self, instance: Post, validated_data):
        tags_data = validated_data.pop("tags_input", [])
        instance = super().update(instance, validated_data)
        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        return instance

    class Meta:
        model = Post
        fields = (
            "id",
            "tags",
            "tags_input",
            "author",
            "content",
            "image",
            "slug",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at", "tags")

    def validate_image(self, value):
        if not value:
            return value
        if value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError(detail="Image size is too large > 5 MB")
        if value.content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(detail="unsupported image type")
        return value
