from django.contrib import admin

from accounts.models import TempExample


@admin.register(TempExample)
class TempExampleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
