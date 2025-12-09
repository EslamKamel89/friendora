from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from accounts.models import Profile, User

admin.site.site_header = "Friendora Admin"
admin.site.site_title = "Friendora Admin"
admin.site.index_title = "Welcome to Friendora Dashboard"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "is_verified",
        "is_superuser",
        "display_name",
        "is_staff",
    )
    list_display_links = ("id", "username", "email", "display_name")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_verified")
    search_fields = ("username", "email", "display_name")
    ordering = ("id",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "user_email", "avatar_thumb", "created_at")
    list_display_links = ("id", "user")
    readonly_fields = ("user", "avatar_preview")

    def user_email(self, obj):
        return obj.user.email

    def avatar_thumb(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:4px;" alt="avatar"/>',
                obj.avatar.url,
            )
        return "(no avatar)"

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-width:220px;height:auto;border-radius:6px;"/>',
                obj.avatar.url,
            )
        return "(no avatar)"

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        qs.select_related("user")
        return qs
