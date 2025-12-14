from rest_framework import serializers

from posts.models import Post

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = ("image/jpeg", "image/png", "image/webp")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    image = serializers.ImageField(
        required=True, allow_null=True, allow_empty_file=True
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "content",
            "image",
            "slug",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

    def validate_image(self, value):
        if not value:
            return value
        if value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError(detail="Image size is too large > 5 MB")
        if value.content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError(detail="unsupported image type")
        return value
