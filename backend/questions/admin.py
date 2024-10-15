from django.contrib import admin, messages

from .models import (
    PollQuestion,
    Question,
    QuestionCondition,
    KeyboardType,
    UserAnswer,
    PollStatus,
)
from .tasks import run_poll_task


class QuestionConditionInline(admin.TabularInline):
    model = QuestionCondition
    fk_name = "question"
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "poll", "text", "question_type", "show", "category_analytics")
    list_filter = ("poll", "category_analytics", "question_type", "show")
    search_fields = ("text",)
    readonly_fields = ("id",)
    inlines = [QuestionConditionInline]

    actions = ["set_show_true", "set_show_false"]

    def set_show_true(self, request, queryset):
        queryset.update(show=True)

    set_show_true.short_description = "Установить show = True для выбранных вопросов"

    def set_show_false(self, request, queryset):
        queryset.update(show=False)

    set_show_false.short_description = "Установить show = False для выбранных вопросов"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "poll",
                    "text",
                    "question_type",
                    "show",
                    "category_analytics",
                )
            },
        ),
    )


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(PollQuestion)
class PollQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "message",
        "get_content_object",
        "intended_for",
        "days_after_hire",
        "time_of_day",
        "intended_for",
        "poll_type",
        "poll_number",
        "is_deleted",
    )
    list_filter = (
        "time_of_day",
        "intended_for",
        "poll_number",
        "poll_type",
        "is_deleted",
    )
    search_fields = ("title", "message", "poll_number")
    readonly_fields = (
        "id",
        "get_content_object",
        "deleted_at",
    )
    actions = ["delete_selected", "hard_delete_pollquestions", "restore_pollquestions"]
    fieldsets = (
        (None, {"fields": ("id", "title", "message")}),
        ("Timing", {"fields": ("days_after_hire", "time_of_day")}),
        (
            "Target",
            {"fields": ("intended_for", "content_type", "get_content_object", "poll_type")},
        ),
        (
            "Информация о создании и обновлении",
            {
                "fields": (
                    "is_deleted",
                    "deleted_at",
                )
            },
        ),
    )

    inlines = [QuestionInline]

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def get_content_object(self, obj):
        if obj.content_object:
            return f"{obj.content_object} (ID: {obj.object_id})"
        return "Not assigned"

    get_content_object.short_description = "Связанный объект"

    def delete_selected(self, request, queryset):
        """Мягкое удаление выбранных шаблонов."""
        deleted_count = 0
        for pollquestion in queryset:
            if not pollquestion.is_deleted:
                pollquestion.delete()
                deleted_count += 1
        self.message_user(
            request, f"Мягко удалено {deleted_count} шаблонов.", messages.SUCCESS
        )

    delete_selected.short_description = "Мягко удалить выбранные шаблоны"

    def hard_delete_pollquestions(self, request, queryset):
        for obj in queryset:
            obj: PollQuestion
            obj.hard_delete()
        self.message_user(
            request, "Выбранные шаблоны были жестко удалены.", messages.SUCCESS
        )

    hard_delete_pollquestions.short_description = "Жестко удалить выбранные шаблоны"

    def restore_pollquestions(self, request, queryset):
        restored_count = 0
        for obj in queryset:
            obj: PollQuestion
            if obj.is_deleted:
                obj.restore()
                restored_count += 1
        self.message_user(
            request, f"Восстановлено {restored_count} шаблонов.", messages.SUCCESS
        )

    restore_pollquestions.short_description = "Восстановить выбранные шаблоны"


@admin.register(KeyboardType)
class KeyboardTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "question_type",
    )
    search_fields = ("question_type",)
    readonly_fields = ("id",)

    fieldsets = ((None, {"fields": ("id", "question_type")}),)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "poll",
        "employee",
        "target_employee",
        "question",
        "answer",
        "created_at",
        "category_analytics",
        "question_type",
    )
    list_filter = (
        "question__poll__intended_for",
        "question__category_analytics",
        "question__question_type",
        "created_at",
        "employee",
        "target_employee",
        "question__poll",
    )
    search_fields = ("answer", "question__poll__title")
    date_hierarchy = "created_at"
    readonly_fields = ("id", "category_analytics", "question_type")

    def poll(self, obj: UserAnswer):
        return str(obj.question.poll)

    poll.short_description = "Опрос"

    def category_analytics(self, obj: UserAnswer):
        return obj.question.get_category_analytics_display()
    
    category_analytics.short_description = "Категория аналитики"
    
    def question_type(self, obj: UserAnswer):
        return obj.question.question_type

    question_type.short_description = "Тип вопроса"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "employee",
                    "target_employee",
                    "question",
                    "answer",
                    "category_analytics",
                    "question_type",
                )
            },
        ),
    )


@admin.register(PollStatus)
class PollStatusAdmin(admin.ModelAdmin):
    actions = ["run_poll"]

    list_display = (
        "id",
        "employee",
        "target_employee",
        "poll",
        "status",
        "started_at",
        "completed_at",
        "date_planned_at",
        "time_planned_at",
        "created_by_admin",
    )
    list_filter = (
        "status",
        "date_planned_at",
        "time_planned_at",
        "employee",
        "target_employee",
        "created_by_admin",
    )
    search_fields = ("employee__full_name", "poll__title")
    readonly_fields = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "employee",
                    "target_employee",
                    "poll",
                    "status",
                    "created_by_admin",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "started_at",
                    "completed_at",
                    "date_planned_at",
                    "time_planned_at",
                )
            },
        ),
    )

    def run_poll(self, request, queryset):
        queryset = queryset.exclude(status=PollStatus.Status.COMPLETED)

        for poll_status in queryset:
            run_poll_task.delay(poll_status.id)

    run_poll.short_description = "Запустить опрос"


@admin.register(QuestionCondition)
class QuestionConditionAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "previous_question", "answer_condition")
    list_filter = ("question", "previous_question", "answer_condition")
    search_fields = ("question__text", "previous_question__text")
    readonly_fields = ("id",)

    fieldsets = (
        (None, {"fields": ("id", "question", "previous_question", "answer_condition")}),
    )
