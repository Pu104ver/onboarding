from django.utils import timezone
from django.db.models.query import QuerySet
from django.http import HttpResponse

from .models import PollStatus, PollQuestion, UserAnswer
from .tasks import run_poll_task
from employees.models import Employee

from datetime import datetime
from io import BytesIO
import pandas as pd
import csv


class PollsService:
    @staticmethod
    def create_poll(
        employee: Employee,
        poll: PollQuestion,
        date_planned_at: datetime,
        target_employee: Employee = None,
    ) -> tuple[PollStatus | None, str | None]:
        """
        Создает опрос для сотрудника.

        Возвращает объект созданного запланированного опроса PollStatus. В случае ошибки возвращает None и сообщение об ошибке (если есть)

        Args:
            employee (Employee): сотрудник
            poll (PollQuestion): опрос
            date_planned_at (datetime): дата запланированного опроса
            target_employee (Optional[Employee]): сотрудник, по которому будет проходить опрос
        Returns:
            tuple ([Optional[PollStatus], str): PollStatus - созданный опрос, str - сообщение об ошибке

        """
        if poll.is_deleted:
            return None, "Невозможно создать опрос. Переданный шаблон был удален."

        if poll.intended_for != employee.role:
            return (
                None,
                f"Опрос предназначен для {poll.get_intended_for_display()}. Роль переданного сотрудника: {employee.get_role_display()}",
            )
        if (
            employee.role == Employee.RoleChoices.EMPLOYEE
            and target_employee is not None
        ):
            return None, "Сотрудник не может иметь опроса по другому сотруднику"
        try:
            employee_poll: PollStatus = PollStatus.objects.get(
                poll=poll, employee=employee, target_employee=target_employee
            )

            if employee_poll:
                return (
                    None,
                    f"Переданный опрос уже создан для данного сотрудника. Существующий опрос - {employee_poll.poll.title} ({employee_poll.get_status_display()})",
                )

        except PollStatus.DoesNotExist:
            pass

        poll_status = PollStatus.objects.create(
            employee=employee,
            target_employee=target_employee,
            poll=poll,
            status=PollStatus.Status.NOT_STARTED,
            date_planned_at=date_planned_at,
            time_planned_at=poll.time_of_day,
            is_archived=False,
            created_by_admin=True,
        )
        if not target_employee:
            employee.update_onboarding_status()

        today = timezone.now().date()
        if date_planned_at == today:
            run_poll_task.delay(poll_status.id)

        return poll_status, None

    @staticmethod
    def filter_users_answers(
        employees_ids: list[int],
        target_employees_ids: list[int],
        questions_ids: list[int],
        polls_ids: list[int],
        poll_status: str,
        answers: QuerySet[UserAnswer] = None,
    ) -> tuple[QuerySet[UserAnswer] | None, str | None]:
        """
        Принимает набор параметров для фильтрации ответов сотрудников и QuerySet ответов (Default - все существующие ответы).

        Возвращает кортеж из QuerySet с отфильтрованными данными, либо None и сообщение об ошибке.

        Args:
            employees (list[int]): список идентификаторов сотрудников
            target_employees (list[int]): список идентификаторов таргет сотрудников
            questions (list[int]): список идентификаторов вопросов
            polls (list[int]): список идентификаторов опросов
            poll_status (str): статус опроса

        Returns:
            tuple ([Optional[QuerySet[UserAnswer]], str]): QuerySet с отфильтрованными данными, error - сообщение об ошибке
        """

        if answers is None:
            answers = (
                UserAnswer.objects.select_related(
                    "employee", "target_employee", "question", "question__poll"
                )
                .prefetch_related("employee__employee_pollstatus")
                .all()
                .distinct()
                .order_by("id")
            )

        if employees_ids:
            answers = answers.filter(employee__in=employees_ids)

        if target_employees_ids:
            answers = answers.filter(target_employee__in=target_employees_ids)

        if questions_ids:
            answers = answers.filter(question__in=questions_ids)

        if polls_ids:
            answers = answers.filter(question__poll__in=polls_ids)

        if poll_status:
            employees = answers.values_list("employee", flat=True)
            target_employees = answers.values_list("target_employee", flat=True)
            polls = answers.values_list("question__poll", flat=True)

            data = list(zip(employees, target_employees, polls))

            # для каждого ответа ищем соответствующий статус опроса
            for employee_id, target_employee_id, poll_id in data:
                try:
                    employee_poll_status: PollStatus = Employee.objects.get(
                        id=employee_id
                    ).employee_pollstatus.get(
                        employee_id=employee_id,
                        target_employee_id=target_employee_id,
                        poll_id=poll_id,
                    )
                except Employee.DoesNotExist:
                    continue
                except PollStatus.DoesNotExist:
                    continue

                if employee_poll_status.status != poll_status:
                    answers = answers.exclude(
                        employee__employee_pollstatus__id=employee_poll_status.id
                    )

        if not answers.exists():
            return None, "Ответы не найдены"

        return answers, None

    @staticmethod
    def generate_csv(
        answers: QuerySet[UserAnswer],
    ) -> tuple[HttpResponse | None, str | None]:
        """
        Генерирует CSV файл с переданными ответами.

        :param answers: QuerySet с отфильтрованными данными
        :return (HttpResponse, str): Кортеж с HttpResponse и с сообщениями об ошибках
        """
        # TODO: разобраться почему возникает a bytes-like object is required, not 'str'
        output = BytesIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "ФИО сотрудника",
                "Вопрос",
                "Ответ",
                "ФИО целевого сотрудника",
                "Требует внимания",
                "Дата и время ответа",
                "Название опроса",
                "Статус опроса",
                "Тип опроса",
                "Связанный объект",
                "Предназначен для",
                "Тип вопроса",
            ],
        )

        writer.writeheader()

        for answer in answers:
            try:
                answer: UserAnswer

                poll_status: PollStatus = answer.employee.employee_pollstatus.filter(
                    target_employee=answer.target_employee, poll=answer.question.poll
                ).first()

                writer.writerow(
                    {
                        "ФИО сотрудника": answer.employee.full_name,
                        "Вопрос": answer.question.text,
                        "ФИО целевого сотрудника": (
                            answer.target_employee.full_name
                            if answer.target_employee
                            else "-"
                        ),
                        "Ответ": answer.answer,
                        "Требует внимания": (
                            "Да" if answer.requires_attention else "Нет"
                        ),
                        "Дата и время ответа": answer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "Название опроса": answer.question.poll.title,
                        "Статус опроса": (
                            poll_status.get_status_display() if poll_status else "-"
                        ),
                        "Тип опроса": answer.question.poll.get_poll_type_display(),
                        "Связанный объект": (
                            answer.question.poll.content_object
                            if answer.question.poll.content_type
                            else "-"
                        ),
                        "Предназначен для": answer.question.poll.get_intended_for_display(),
                    }
                )

            except AttributeError as e:
                return None, f"Ошибка доступа к атрибутам при генерации CSV: {str(e)}"
            except Exception as e:
                return None, f"Неизвестная ошибка при генерации CSV: {str(e)}"

        output.seek(0)
        file_content = output.getvalue()

        response = HttpResponse(file_content, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="employee_answers.csv"'

        return response, None

    @staticmethod
    def generate_excel(
        answers: QuerySet[UserAnswer],
    ) -> tuple[HttpResponse | None, str | None]:
        """
        Генерирует Excel файл с переданными ответами.

        :param answers: QuerySet с отфильтрованными данными
        :return (HttpResponse, str): Кортеж с HttpResponse и с сообщениями об ошибках
        """

        data = []

        for answer in answers:
            try:
                answer: UserAnswer
                poll_status: PollStatus = answer.employee.employee_pollstatus.filter(
                    target_employee=answer.target_employee, poll=answer.question.poll
                ).first()

                data.append(
                    {
                        "ФИО сотрудника": answer.employee.full_name,
                        "Вопрос": answer.question.text,
                        "Ответ": answer.answer,
                        "ФИО целевого сотрудника": (
                            answer.target_employee.full_name
                            if answer.target_employee
                            else "-"
                        ),
                        "Требует внимания": (
                            "Да" if answer.requires_attention else "Нет"
                        ),
                        "Дата и время ответа": answer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "Название опроса": answer.question.poll.title,
                        "Статус опроса": (
                            poll_status.get_status_display() if poll_status else "-"
                        ),
                        "Тип опроса": answer.question.poll.get_poll_type_display(),
                        "Связанный объект": (
                            answer.question.poll.content_object
                            if answer.question.poll.content_object
                            else "-"
                        ),
                        "Предназначен для": answer.question.poll.get_intended_for_display(),
                    }
                )

            except AttributeError as e:
                return None, f"Ошибка доступа к атрибутам при генерации Excel: {str(e)}"
            except Exception as e:
                return None, f"Неизвестная ошибка при генерации Excel: {str(e)}"

            if not data:
                return None, "Нет данных для генерации Excel."

        df = pd.DataFrame(data)
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Ответы сотрудников")

        output.seek(0)
        file_content = output.getvalue()

        response = HttpResponse(
            file_content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="employee_answers.xlsx"'

        return response, None
