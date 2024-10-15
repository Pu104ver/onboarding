from django.contrib import admin, messages
from .models import Employee, CuratorEmployees
from projects.models import ProjectAssignment


class ProjectAssignmentInline(admin.TabularInline):
    model = ProjectAssignment
    extra = 1


class CuratorEmployeesInline(admin.TabularInline):
    model = CuratorEmployees
    fk_name = "employee"
    extra = 1


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "role",
        "full_name",
        "date_of_employment",
        "date_of_dismission",
        "projects_list",
        "curators_list",
        "telegram_nickname",
        "telegram_user_id",
        "is_curator_employee",
        "is_archived",
        "is_deleted",
        "created_at",
        "updated_at",
        "status",
        "risk_status",
        "date_meeting",
        "description",
        "onboarding_status",
    )
    list_filter = (
        "is_archived",
        "role",
        "is_curator_employee",
        "status",
        "risk_status",
        "date_meeting",
        "date_of_employment",
        "date_of_dismission",
        "created_at",
        "updated_at",
    )
    search_fields = ("full_name", "description")
    inlines = [ProjectAssignmentInline, CuratorEmployeesInline]
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
        "deleted_at",
        "onboarding_status",
    )
    actions = [
        "archive_employees",
        "unarchive_employees",
        "delete_selected",
        "hard_delete_employees",
        "restore_employees",
        "update_employees_onboarding_status",
    ]

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def delete_selected(self, request, queryset):
        """Мягкое удаление выбранных сотрудников."""
        deleted_count = 0
        for employee in queryset:
            if not employee.is_deleted:
                employee.delete()
                deleted_count += 1
        self.message_user(
            request, f"Мягко удалено {deleted_count} сотрудников.", messages.SUCCESS
        )

    delete_selected.short_description = "Мягко удалить выбранных сотрудников"

    def archive_employees(self, request, queryset):
        queryset.update(is_archived=True)

    archive_employees.short_description = "Архивировать выбранных сотрудников"

    def unarchive_employees(self, request, queryset):
        queryset.update(is_archived=False)

    unarchive_employees.short_description = "Разархивировать выбранных сотрудников"

    def projects_list(self, obj):
        return ", ".join(
            [assignment.project.name for assignment in obj.projects_assigned.all()]
        )

    projects_list.short_description = "Проекты"

    def curators_list(self, obj):
        return ", ".join([curator.curator.full_name for curator in obj.curators.all()])

    curators_list.short_description = "Кураторы"

    def hard_delete_employees(self, request, queryset):
        for obj in queryset:
            obj: Employee
            obj.hard_delete()
        self.message_user(
            request, "Выбранные сотрудники были жестко удалены.", messages.SUCCESS
        )

    hard_delete_employees.short_description = "Жестко удалить выбранных сотрудников"

    def restore_employees(self, request, queryset):
        restored_count = 0
        for obj in queryset:
            obj: Employee
            if obj.is_deleted:
                obj.restore()
                restored_count += 1
        self.message_user(
            request, f"Восстановлено {restored_count} сотрудников.", messages.SUCCESS
        )

    restore_employees.short_description = "Восстановить выбранных сотрудников"

    def update_employees_onboarding_status(self, request, queryset):
        updated_count = 0
        for obj in queryset:
            obj: Employee
            obj.update_onboarding_status()
            updated_count += 1
        self.message_user(
            request, f"Обновлено {updated_count} сотрудников.", messages.SUCCESS
        )

    update_employees_onboarding_status.short_description = "Обновить статус сотрудников"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "user",
                    "role",
                    "full_name",
                    "description",
                    "date_of_employment",
                    "date_of_dismission",
                    "telegram_nickname",
                    "telegram_user_id",
                    "status",
                    "risk_status",
                    "onboarding_status",
                    "date_meeting",
                    "is_curator_employee",
                )
            },
        ),
        ("Статус", {"fields": ("is_archived",)}),
        (
            "Информация о создании и обновлении",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_by",
                    "updated_at",
                    "deleted_at",
                )
            },
        ),
    )


@admin.register(CuratorEmployees)
class CuratorEmployeesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "curator",
        "employee",
    )
    search_fields = ("curator__full_name", "employee__full_name")
    list_filter = (
        "curator",
        "employee",
    )
    ordering = ("-id",)
    readonly_fields = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "curator",
                    "employee",
                )
            },
        ),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("curator", "employee")
