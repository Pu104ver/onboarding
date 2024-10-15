from django.contrib import admin, messages
from .models import FeedbackUser


@admin.register(FeedbackUser)
class FeedbackUserAdmin(admin.ModelAdmin):
    list_display = ["id", "employee", "text", "created_at", "is_deleted"]
    search_fields = ["text", "employee__full_name"]
    list_filter = ["created_at", "employee", "is_deleted"]
    readonly_fields = ["id", "created_at", "deleted_at", "is_deleted"]

    actions = [
        "delete_selected",
        "hard_delete_feedback",
        "restore_feedback",
    ]

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def delete_selected(self, request, queryset):
        """Мягкое удаление выбранных фидбеков."""
        deleted_count = 0
        for feedback in queryset:
            if not feedback.is_deleted:
                feedback.delete()
                deleted_count += 1
        self.message_user(
            request, f"Мягко удалено {deleted_count} фидбеков.", messages.SUCCESS
        )

    delete_selected.short_description = "Мягко удалить выбранные фидбеки"

    def hard_delete_feedback(self, request, queryset):
        for feedback in queryset:
            feedback.hard_delete()
        self.message_user(
            request, "Выбранные фидбеки были жестко удалены.", messages.SUCCESS
        )

    hard_delete_feedback.short_description = "Жестко удалить выбранные фидбеки"

    def restore_feedback(self, request, queryset):
        restored_count = 0
        for feedback in queryset:
            if feedback.is_deleted:
                feedback.restore()
                restored_count += 1
        self.message_user(
            request, f"Восстановлено {restored_count} фидбеков.", messages.SUCCESS
        )

    restore_feedback.short_description = "Восстановить выбранные фидбеки"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "employee",
                    "text",
                ),
            },
        ),
        (
            "Дополнительная информация",
            {
                "fields": ("created_at", "is_deleted", "deleted_at"),
            },
        ),
    )
