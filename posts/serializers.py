from datetime import datetime
from typing import Optional, Required

from rest_framework import serializers

from posts.models import Like, Post, Report, Tag
from posts.types import ReportSummaryInput

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
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)

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
            "likes_count",
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


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")
        read_only_fields = ("id", "user", "post", "created_at")


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ("post", "reason")


class ReportSummarySerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    post_author = serializers.CharField()
    post_content = serializers.CharField()
    reports_count = serializers.SerializerMethodField()
    report_reasons = serializers.SerializerMethodField()
    last_reported_at = serializers.SerializerMethodField()
    is_action_taken = serializers.SerializerMethodField()

    def get_is_action_taken(self, obj: ReportSummaryInput) -> bool:
        return obj["reports"].filter(status=Report.Status.ACTION_TAKEN).exists()

    def get_reports_count(self, obj: ReportSummaryInput) -> int:
        return obj["reports"].count()

    def get_report_reasons(self, obj: ReportSummaryInput) -> list[str]:
        # return [report.reason for report in obj["reports"]]
        return list(obj["reports"].values_list("reason", flat=True))

    def get_last_reported_at(self, obj: ReportSummaryInput) -> Optional[datetime]:
        latest = obj["reports"].order_by("-created_at").first()
        return latest.created_at if latest else None

    def to_representation(self, instance: ReportSummaryInput):
        data = super().to_representation(instance)
        data["reports_count"] = len(data["report_reasons"])
        return data
