from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "author", "created_at")
    list_filter = ("created_at", "employee")
    search_fields = ("author__full_name", "employee__full_name", "text")
    readonly_fields = ("id", "created_at", "updated_at", "updated_by")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "employee",
                    "author",
                    "text",
                ),
            },
        ),
        (
            "Дополнительная информация",
            {
                "fields": ("created_at", "updated_at", "updated_by"),
            },
        ),
    )
