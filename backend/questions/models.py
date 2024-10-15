from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from datetime import timedelta, datetime

from core.models import SoftDeleteModel
from questions.managers import ActivePollStatusManager


class QuestionType(models.TextChoices):
    """
    Типы вопросов.
    """

    YES_NO = "yes_no", "Yes/No"
    FINISH = "finish", "Finish"
    MESSAGE = "message", "Message"
    NEXT = "next", "Next"
    NUMBERS = "numbers", "Numbers"
    SLOTS = "slots", "Slots"


class TimeOfDay(models.TextChoices):
    """
    Временные рамки когда пользователя уведомляет бот
    morning - 9 часов
    evening - 18 часов
    """

    MORNING = "morning", "Утро"
    EVENING = "evening", "Вечер"


class UserType(models.TextChoices):
    """
    Пулы опросов разделены на Choices
    """

    EMPLOYEE = "employee", "Сотрудник"
    CURATOR = "curator", "Куратор"


class PollType(models.TextChoices):
    ONBOARDING = "onboarding", "Онбординг"
    OFFBOARDING = "offboarding", "Офбординг"
    FEEDBACK = "feedback", "Обратная связь"
    INTERMEDIATE_FEEDBACK = "intermediate_feedback", "Промежуточная обратная связь"


class EmployeeCategoryAnalytics(models.TextChoices):
    GENERAL_HEALTH = "general_health", "Общее самочувствие"
    RESPONSIBILITIES = "responsibilities", "Понимание обязанностей и функционала"
    JOB_EXPECTATIONS = "job_expectations", "Ожидания от работы"
    TEAM_SATISFACTIONS = "team_satisfactions", "Удовлетворенность командой"
    ONBOARDING_SATISFACTIONS = (
        "onboarding_satisfactions",
        "Удовлетворенность онбордингом",
    )
    INTEREST_PROJECT = "interest_project", "Заинтересованность проектом"
    QUALITY_FEEDBACK = "quality_feedback", "Качество обратной связи"
    PROJECT_EXPECTATIONS = "project_expectations", "Ожидания от проекта"
    UNDERSTAND_TASKS_DEADLINES = (
        "understand_tasks_deadlines",
        "Понимание задач и сроков",
    )


class CuratorCategoryAnalytics(models.TextChoices):
    DISCIPLINE = "discipline", "Дисциплина"
    QUALITY_TASKS = "quality_tasks", "Качество задач"
    QUALITY_INTERACTIONS = "quality_interactions", "Качество взаимодействия"
    INVOLVEMENT = "involvement", "Вовлеченность"


class PollQuestion(SoftDeleteModel):
    """
    Модель опросов.

    Attributes:
        title (CharField): Название опроса (напр.: 1-й день).
        message (TextField): Сообщение, приходящее вместе с кнопкой начала опроса.
        days_after_hire (IntegerField): Количество дней после устройства сотрудника, когда должен начаться опрос.
        time_of_day (CharField): Время суток для начала опроса.
        intended_for (CharField): Метка для кого предзначен опрос (Куратор/Сотрудник).
        poll_type (CharField): Тип опроса
        poll_number (PositiveIntegerField): Порядковый номер опроса
        content_type (ForeignKey): Ссылка на ContentType
        object_id (PositiveIntegerField): Идентификатор объекта
        content_object (GenericForeignKey): Обобщенная связь с объектом
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Название опроса",
    )
    message = models.TextField(
        verbose_name="Сообщение старта опроса",
        max_length=1024,
        default="Ответь на несколько вопросов",
    )
    days_after_hire = models.IntegerField(
        verbose_name="Дни после устройства",
        help_text="Количество дней после даты устройства сотрудника, когда должен начаться опрос",
        default=0,
    )
    time_of_day = models.CharField(
        max_length=10,
        choices=TimeOfDay.choices,
        default=TimeOfDay.MORNING,
        verbose_name="Время суток начала опроса",
    )
    intended_for = models.CharField(
        verbose_name="Предназначен для",
        choices=UserType.choices,
        default=UserType.EMPLOYEE,
    )

    poll_type = models.CharField(
        max_length=50,
        choices=PollType.choices,
        default=PollType.ONBOARDING,
        verbose_name="Тип опроса",
    )

    poll_number = models.PositiveIntegerField(
        verbose_name="Порядковый номер опроса",
        default=1,
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )

    object_id = models.PositiveIntegerField(null=True, blank=True)

    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        return f"{self.title} - {self.content_object} ({self.intended_for})"

    class Meta:
        verbose_name = "Шаблон опроса"
        verbose_name_plural = "Шаблоны опросов"


class Question(models.Model):
    """
    Модель вопросов.

    Attributes:
        poll (ForeignKey): Привязка вопроса к опросу.
        text (TextField): Текст вопроса.
        question_type (CharField): Тип вопроса из choices.
        category_analytics (CharField): Категория аналитики
        show (BooleanField): Показывать вопрос

    """

    poll = models.ForeignKey(
        PollQuestion,
        related_name="questions",
        on_delete=models.CASCADE,
        verbose_name="Опрос",
    )
    text = models.TextField(max_length=1024, verbose_name="Текст вопроса")
    question_type = models.CharField(
        max_length=50, choices=QuestionType.choices, verbose_name="Тип вопроса"
    )

    category_analytics = models.CharField(
        max_length=30,
        choices=list(EmployeeCategoryAnalytics.choices) + list(CuratorCategoryAnalytics.choices),
        default=None,
        blank=True,
        null=True,
        verbose_name="Категория аналитики",
    )

    # раньше думали, что фронты будут фильтроваться по этому полю
    show = models.BooleanField(
        default=True,
        verbose_name="Показывать вопрос",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.text


class QuestionCondition(models.Model):
    """
    Модель условий вопросов.

    Attributes:
        question (ForeignKey): Следующий вопрос.
        previous_question (ForeignKey): Предыдущий вопрос.
        answer_condition (CharField): Условие появление следующего вопроса из предыдущего
    """

    class AnswerType(models.TextChoices):
        YES = "yes", "Да"
        NO = "no", "Нет"
        SOME_TEXT = "some_text", "Некоторый текст"
        NEXT = "next", "Следующий"
        ONE = "1", "1"
        TWO = "2", "2"
        THREE = "3", "3"
        FOUR = "4", "4"
        FIVE = "5", "5"

    question = models.ForeignKey(
        Question,
        related_name="conditions",
        on_delete=models.CASCADE,
        verbose_name="Вопрос",
    )

    previous_question = models.ForeignKey(
        Question,
        related_name="previous_conditions",
        on_delete=models.CASCADE,
        verbose_name="Предыдущий вопрос",
    )
    answer_condition = models.CharField(
        max_length=255, choices=AnswerType.choices, verbose_name="Условие"
    )

    class Meta:
        unique_together = ("question", "previous_question", "answer_condition")
        verbose_name = "Условие вопроса"
        verbose_name_plural = "Условия вопросов"

    def __str__(self):
        return f'Вопрос "{self.question.id}" идет после вопроса "{self.previous_question.id}" если ответ был "{self.answer_condition}"'


class KeyboardType(models.Model):
    """
    Модель инлайн-клавиатур для вопросов.

    Attributes:
        question_type (CharField): Тип вопроса (такие же как в модели Question).
        keyboard_json (JSONField): Клавиатура в формате JSON.
    """

    question_type = models.CharField(
        max_length=50,
        choices=QuestionType.choices,
        unique=True,
        verbose_name="Тип вопроса",
    )
    keyboard_json = models.JSONField()

    class Meta:
        verbose_name = "Клавиатура"
        verbose_name_plural = "Клавиатуры"


class UserAnswer(models.Model):
    """
    Модель ответов.

    Attributes:
        employee (ForeignKey): Сотрудник, давший ответ.
        target_employee (ForeignKey): Сотрудник, к кому был привязан вопрос (null в случае если ответ от самого сотрудника)
        question (ForeignKey): Вопрос на который был дан ответ
        answer (TextField): Ответ на вопрос
        requires_attention (BooleanField): Флаг плохого ответа
        created_at (DateTimeField): Дата ответа
    """

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        verbose_name="Сотрудник",
        related_name="employee_useranswer",
    )
    target_employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Сотрудник, по которому был дан ответ",
        related_name="target_employee_useranswer",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name="Вопрос"
    )
    answer = models.TextField(max_length=1024, verbose_name="Ответ")
    requires_attention = models.BooleanField(
        default=False, verbose_name="Требует внимания"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата ответа")

    def __str__(self):
        return f'Ответ пользователя {self.employee.full_name} на вопрос "{self.question.text}"'

    class Meta:
        unique_together = ("employee", "target_employee", "question")
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"


class PollStatus(models.Model):
    """
    Модель для отслеживания статуса прохождения опроса сотрудником.

    Attributes:
        employee (ForeignKey): Пользователь, чей опрос
        target_employee (ForeignKey): Сотрудник, к которому привязан опрос (null если опрос для сотрудника).
        poll (ForeignKey): Опрос, который проходит сотрудник.
        status (CharField): Статус прохождения опроса (не начат, в процессе, завершен, заморожен).
        started_at (DateTimeField): Дата и время начала опроса.
        completed_at (DateTimeField): Дата и время завершения опроса.
        date_planned_at (DateField): Дата когда пользователю будет предложен опрос
        time_planned_at (CharField): Время когда пользователю будет предложен опрос
        created_by_admin (BooleanField): Флаг создания опроса администратором
        is_archived (BooleanField): Флаг архивации опроса
    """

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Не начат"
        IN_PROGRESS = "in_progress", "В процессе"
        IN_FROZEN = "in_frozen", "Заморожен"
        EXPIRED = "expired", "Просрочен"
        COMPLETED = "completed", "Завершен"

    employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        verbose_name="Сотрудник",
        related_name="employee_pollstatus",
    )

    target_employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Сотрудник по которому происходит опрос",
        related_name="target_employee_pollstatus",
    )

    poll = models.ForeignKey(
        PollQuestion, on_delete=models.CASCADE, verbose_name="Опрос"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED,
        verbose_name="Статус",
    )
    started_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата и время начала"
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата и время завершения"
    )
    date_planned_at = models.DateField(
        null=True, blank=True, verbose_name="Дата уведомления"
    )
    time_planned_at = models.CharField(
        null=True,
        blank=True,
        verbose_name="Время суток уведомления",
        choices=TimeOfDay.choices,
    )

    created_by_admin = models.BooleanField(
        default=False, verbose_name="Создано администратором"
    )

    is_archived = models.BooleanField(default=False, verbose_name="В архиве")

    objects = ActivePollStatusManager()
    all_objects = models.Manager()

    class Meta:
        unique_together = ("employee", "poll", "target_employee")
        verbose_name = "Статус опроса"
        verbose_name_plural = "Статусы опросов"

    def __str__(self):
        return f"{self.employee} - {self.poll} - {self.status}"

    def save(self, *args, **kwargs):
        """
        Метод сохранения даты и время запланированных опросов
        Если опрос устанавливается для сотрудника, то время опроса рассчитывается от дня его устройства на работу
        Если опрос устанавливается для куратора, то время опроса рассчитывается от дня устройства сотрудника (target_employee)
        """
        if self.date_planned_at is None or self.time_planned_at is None:
            start_date = None
            employee_date_of_employment = self.employee.date_of_employment

            if employee_date_of_employment:
                if not self.target_employee:
                    start_date = (
                        datetime.strptime(employee_date_of_employment, "%Y-%m-%d")
                        if type(employee_date_of_employment) == str
                        else employee_date_of_employment
                        + timedelta(days=self.poll.days_after_hire)
                    )
                else:
                    target_employee_date_of_employment = (
                        self.target_employee.date_of_employment
                    )
                    if target_employee_date_of_employment:
                        start_date = (
                            datetime.strptime(
                                target_employee_date_of_employment, "%Y-%m-%d"
                            )
                            if type(target_employee_date_of_employment) == str
                            else target_employee_date_of_employment
                            + timedelta(days=self.poll.days_after_hire)
                        )

                self.date_planned_at = start_date
                self.time_planned_at = self.poll.time_of_day
        super().save(*args, **kwargs)
