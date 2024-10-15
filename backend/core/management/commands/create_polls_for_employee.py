from django.core.management.base import BaseCommand, CommandParser
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models.query import QuerySet
from projects.models import Project, ProjectAssignment
from employees.models import Employee
from questions.models import PollQuestion
from questions.services import PollsService
from typing import Any


class Command(BaseCommand):
    help = "Создает запланированные опросы для сотрудника. Важно чтобы у сотрудника был назначен проект и куратор для соответствующего опроса."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("employee_id", type=int, help="ID сотрудника")
        parser.add_argument("poll_id", type=int, help="ID опроса")
        parser.add_argument(
            "--date_planned_at",
            type=str,
            help="Дата запланированного опроса",
            default=None,
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            employee_id = options["employee_id"]
            poll_id = options["poll_id"]
            date_planned_at = options["date_planned_at"]
            if not date_planned_at:
                date_planned_at: str = timezone.now().strftime("%Y-%m-%d")

            if not employee_id or not poll_id:
                self.stderr.write(
                    self.style.ERROR("Необходимо указать ID сотрудника и ID опроса.")
                )

            employee = Employee.objects.get(id=employee_id)
            if not employee:
                self.stderr.write(
                    self.style.ERROR(f"Сотрудник {employee} (ID {employee_id}) не найден.")
                )
                return None
            if employee.role != Employee.RoleChoices.EMPLOYEE:
                self.stderr.write(
                    self.style.ERROR(f"Сотрудник {employee} должен иметь роль EMPLOYEE.")
                )
                return None

            employee_projects_assigned: QuerySet[ProjectAssignment] = (
                employee.projects_assigned.all()
            )

            poll: PollQuestion = PollQuestion.objects.get(id=poll_id)
            poll_content_type = poll.content_type

            employee_projects_ids = employee_projects_assigned.values_list(
                "project_id", flat=True
            )
            if (
                poll_content_type
                == ContentType.objects.get_for_model(Project)
                and poll.object_id not in employee_projects_ids
            ):
                self.stderr.write(
                    self.style.ERROR(
                        f"Сотрудник {employee} не пренадлежит проекту с ID {poll.object_id}."
                    )
                )
                return None

            poll_status, error = PollsService.create_poll(
                employee=employee,
                poll=poll,
                date_planned_at=date_planned_at,
            )
            if error is not None:
                self.stderr.write(self.style.ERROR(error["error"]))
                self.stderr.write(self.style.ERROR(error["detail"]))
                return None

            return f"Опрос успешно создан: {poll_status}"

        except PollQuestion.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Опрос с ID {poll_id} не найден."))
            return None
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Произошла ошибка: {e}"))
            return None
