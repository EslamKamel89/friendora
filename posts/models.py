from typing import TYPE_CHECKING, Iterable

from django.conf import settings
from django.db import models
from django.utils import timezone

from common.utils import unique_slug

if TYPE_CHECKING:
    from accounts.models import User


class PostManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("author")


class Post(models.Model):
    id: int
    author: "User" = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )  # type: ignore
    content = models.TextField()
    image = models.ImageField(upload_to="posts", blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = PostManager()
    raw = models.Manager()
    tags = models.ManyToManyField("Tag", related_name="posts", blank=True)  # type: ignore

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
