from asyncio import constants
from typing import TYPE_CHECKING, Iterable, Self

from django.conf import settings
from django.db import models
from django.utils import timezone

from accounts.models import User
from common.utils import unique_slug


class PostManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("author")


class Post(models.Model):
    id: int
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    image = models.ImageField(upload_to="posts", blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PostManager()
    raw = models.Manager()
    tags = models.ManyToManyField("Tag", related_name="posts", blank=True)

    class Meta:
        ordering = ("-created_at",)

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = unique_slug(
                self.content[:50] or f"post-{timezone.now().timestamp()}"
            )
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"post {self.id} by {self.author.username}"


class Tag(models.Model):
    id: int
    name = models.CharField(max_length=100, unique=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class LikeQuerySet(models.QuerySet):
    def with_user_post(self) -> Self:
        return self.select_related("post", "user")


class Like(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    objects = LikeQuerySet.as_manager()

    def __str__(self) -> str:
        return f"{self.user} likes post id: {self.post.id} "

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_user_post")
        ]
        ordering = ("-created_at",)


class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = ("pending", "Pending")
        REVIEWED = ("reviewed", "Reviewed")
        ACTION_TAKEN = ("action_taken", "Action Taken")

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports")
    reason = models.TextField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reporter", "post"], name="unique_report_per_user_per_post"
            )
        ]

    def __str__(self) -> str:
        return f"Report by {self.reporter_id} on post {self.post_id}"  # type: ignore
