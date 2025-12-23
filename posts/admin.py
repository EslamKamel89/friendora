from django.contrib import admin
from django.utils.html import format_html

from posts.models import Post, Tag


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "id",
        "author",
        "image",
        "short_content",
        "published",
        "created_at",
        "updated_at",
    )
    # autocomplete_fields = ("tags",)
    filter_horizontal = ("tags",)
    # readonly_fields = ("image_preview",)
    list_display_links = ("id", "short_content")

    def short_content(self, obj: Post):
        return obj.content[:70] + "...." if len(obj.content) > 70 else obj.content

    def image_preview(self, obj: Post):
        return format_html(
            '<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:4px;" alt="avatar"/>',
            obj.image.url,
        )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)
