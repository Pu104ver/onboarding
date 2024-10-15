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
    help = "Создает запланированные опросы для куратора. Важно чтобы у куратора был назначен проект и сотрудник для соответствующего опроса."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("curator_id", type=int, help="ID куратора")
        parser.add_argument("poll_id", type=int, help="ID опроса")
        parser.add_argument("target_employee_id", type=int, help="ID таргет сотрудника")
        parser.add_argument(
            "--date_planned_at",
            type=str,
            help="Дата запланированного опроса",
            default=None,
        )

    def handle(self, *args: Any, **options: Any) -> str | None:
        try:
            curator_id = options["curator_id"]
            poll_id = options["poll_id"]
            target_employee_id = options["target_employee_id"]
            date_planned_at = options["date_planned_at"]

            if not curator_id or not poll_id:
                self.stderr.write(
                    self.style.ERROR("Необходимо указать ID куратора и ID опроса.")
                )

            curator: Employee = Employee.objects.get(id=curator_id)
            if not curator:
                self.stderr.write(
                    self.style.ERROR(f"Куратор с ID {curator_id} не найден.")
                )
                return None
            if curator.role != Employee.RoleChoices.CURATOR:
                self.stderr.write(
                    self.style.ERROR(f"Куратор {curator} должен иметь роль CURATOR.")
                )
                return None

            curator_projects_assigned: QuerySet[ProjectAssignment] = (
                curator.projects_assigned.all()
            )

            poll: PollQuestion = PollQuestion.objects.get(id=poll_id)
            poll_content_type = poll.content_type

            curator_projects_ids = curator_projects_assigned.values_list(
                "project_id", flat=True
            )
            if (
                poll_content_type
                == ContentType.objects.get_for_model(Project)
                and poll.object_id not in curator_projects_ids
            ):
                self.stderr.write(
                    self.style.ERROR(
                        f"Куратор {curator} не пренадлежит проекту с ID {poll.object_id}."
                    )
                )
                return None

            curator_employees = curator.employees.all()
            if not curator_employees.exists():
                self.stderr.write(
                    self.style.ERROR(f"Куратор {curator} должен иметь хотя бы одного сотрудника.")
                )
                return None

            target_employee = Employee.objects.get(id=target_employee_id)
            if not target_employee:
                self.stderr.write(
                    self.style.ERROR(f"Сотрудник с ID {target_employee_id} не найден.")
                )
                return None
            if target_employee.role != Employee.RoleChoices.EMPLOYEE:
                self.stderr.write(
                    self.style.ERROR(f"Сотрудник {target_employee} должен иметь роль EMPLOYEE.")
                )
                return None
            if target_employee.id not in curator_employees.values_list(
                "employee_id", flat=True
            ):
                self.stderr.write(
                    self.style.ERROR(
                        f"Сотрудник {target_employee} ({target_employee_id}) не пренадлежит куратору."
                    )
                )
                return None

            target_employee_projects_assigned = target_employee.projects_assigned.all()
            if not target_employee_projects_assigned.exists():
                self.stderr.write(
                    self.style.ERROR(
                        f"Сотрудник {target_employee} должен иметь хотя бы один проект."
                    )
                )
                return None
            target_employee_projects_ids = (
                target_employee_projects_assigned.values_list("project_id", flat=True)
            )
            if (
                poll_content_type == "projects"
                and poll.object_id not in target_employee_projects_ids
            ):
                self.stderr.write(
                    self.style.ERROR(
                        f"Сотрудник {target_employee} не пренадлежит проекту с ID {poll.object_id}."
                    )
                )
                return None

            if not date_planned_at:
                date_planned_at: str = timezone.now().strftime("%Y-%m-%d")

            poll_status, error = PollsService.create_poll(
                employee=curator,
                poll=poll,
                target_employee=target_employee,
                date_planned_at=date_planned_at,
            )

            if error is not None:
                self.stderr.write(self.style.ERROR(error["error"]))
                return None

            return f"Опрос успешно создан: {poll_status}"

        except PollQuestion.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Опрос с ID {poll_id} не найден."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Произошла ошибка: {e}"))
            return None
