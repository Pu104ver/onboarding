from django.contrib import admin, messages
from .models import Project, ProjectAssignment


class ProjectAssignmentInline(admin.TabularInline):
    model = ProjectAssignment
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "employees_count",
        "employees_list",
        "date_start",
        "date_end",
        "created_at",
        "updated_at",
        "is_deleted",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("name",)
    inlines = [ProjectAssignmentInline]
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "deleted_at",
    )

    actions = [
        "hard_delete_projects",
        "delete_selected",
        "restore_projects",
    ]

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def delete_selected(self, request, queryset):
        """Мягкое удаление выбранных проектов."""
        deleted_count = 0
        for employee in queryset:
            if not employee.is_deleted:
                employee.delete()
                deleted_count += 1
        self.message_user(
            request, f"Мягко удалено {deleted_count} проектов.", messages.SUCCESS
        )

    delete_selected.short_description = "Мягко удалить выбранные проекты"

    def employees_count(self, obj: Project):
        return obj.employees_assigned.all().count()

    employees_count.short_description = "Количество сотрудников"

    def employees_list(self, obj: Project):
        return ", ".join(
            [str(assignment.employee) for assignment in obj.employees_assigned.all()]
        )

    employees_list.short_description = "Список сотрудников"

    def hard_delete_projects(self, request, queryset):
        for obj in queryset:
            obj.hard_delete()
        self.message_user(
            request, "Выбранные проекты были жестко удалены.", messages.SUCCESS
        )

    hard_delete_projects.short_description = "Жестко удалить выбранные проекты"

    def restore_projects(self, request, queryset):
        restored_count = 0
        for obj in queryset:
            if obj.is_deleted:
                obj.restore()
                restored_count += 1
        self.message_user(
            request, f"Восстановлено {restored_count} проектов.", messages.SUCCESS
        )

    restore_projects.short_description = "Восстановить выбранные проекты"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "name",
                    "date_start",
                    "date_end",
                )
            },
        ),
        (
            "Информация о создании и обновлении",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "created_by",
                    "updated_by",
                    "deleted_at",
                ),
            },
        ),
    )


@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "project", "date_of_employment")
    search_fields = ("employee__full_name", "project__name")
    list_filter = (
        "employee",
        "project",
    )
    readonly_fields = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "employee",
                    "project",
                    "date_of_employment",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("employee", "project")
