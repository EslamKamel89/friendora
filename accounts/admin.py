from django.contrib import admin

from accounts.models import TempExample

admin.site.site_header = "Friendora Admin"
admin.site.site_title = "Friendora Admin"
admin.site.index_title = "Welcome to Friendora Dashboard"


@admin.register(TempExample)
class TempExampleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)
