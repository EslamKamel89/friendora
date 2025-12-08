from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import User

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
