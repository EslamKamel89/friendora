from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id: int
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.username or self.email


class Profile(models.Model):
    id: int
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/default-avatar.png", blank=True
    )
    bio = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile of {self.user.username}"


class FollowQuerySet(models.QuerySet):
    def with_follower(self):
        return self.select_related("follower")

    def with_following(self):
        return self.select_related("following")

    def with_both(self):
        return self.select_related(["follower", "following"])


class Follow(models.Model):
    follower = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="following_set",
        db_index=True,
    )  # i am following these users
    following = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="followers_set",
        db_index=True,
    )  # users who follows me
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = FollowQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follower_following"
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="prevent_self_follow",
            ),
        ]
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.follower} -> {self.following}"
