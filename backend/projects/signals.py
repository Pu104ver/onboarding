from datetime import datetime
from django.contrib.contenttypes.models import ContentType
from projects.models import Project, ProjectAssignment
from questions.utils import create_questions, create_conditions
from questions.models import PollStatus, PollQuestion, UserType, EmployeeCategoryAnalytics, CuratorCategoryAnalytics
from django.db.models import Q
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from questions.tasks import schedule_create_pollstatus_onboarding


@receiver(pre_save, sender=ProjectAssignment)
def project_assignment_date_changed(sender, instance, **kwargs):
    """При добавление даты начала работы сотрудника в проекте - планируем опросы адаптации в проекте от этой даты
    Также планируем опросы для кураторов этого сотрудника"""
    if instance.pk:
        schedule_create_pollstatus_onboarding.delay(instance.pk)


@receiver(post_save, sender=ProjectAssignment)
def set_date_of_employment(sender, instance: ProjectAssignment, created, **kwargs):
    """Устанавливает дату начала работы сотрудника в проекте после создания записи."""
    if created and instance.date_of_employment is None:
        instance.date_of_employment = (
            datetime.strptime(instance.employee.date_of_employment, "%Y-%m-%d")
            if type(instance.employee.date_of_employment) == str
            else instance.employee.date_of_employment
        )
        instance.save(update_fields=["date_of_employment"])


@receiver(post_delete, sender=ProjectAssignment)
def project_assignment_deleted(sender, instance: ProjectAssignment, **kwargs):
    """
    При удаление сотрудника с проекта - удаляет все запланированные опросы по этому проекту для сотрудника
    и его кураторов
    """
    project = instance.project
    employee = instance.employee

    content_type = ContentType.objects.get_for_model(Project)

    PollStatus.objects.filter(
        Q(
            employee=employee,
            poll__content_type=content_type,
            poll__object_id=project.id,
        )
        | Q(
            target_employee=employee,
            poll__content_type=content_type,
            poll__object_id=project.id,
        )
    ).delete()

    employee.update_onboarding_status()

@receiver(post_save, sender=Project)
def project_deleted(sender, instance: Project, **kwargs):
    """
    При удалении проекта - удаляет все шаблоны и запланированные опросы (CASCADE при удалении PollQuestion, то есть шаблонов) по этому проекту
    """
    if instance.is_deleted:
        PollQuestion.objects.filter(
            content_type=ContentType.objects.get_for_model(Project),
            object_id=instance.id,
        ).delete()


@receiver(post_save, sender=Project)
def create_pollquestion_for_project(sender, instance, created, **kwargs):
    """
    Создает новые опросы адаптации для проекта при создании нового проекта
    """
    if created:
        project_content_type = ContentType.objects.get_for_model(Project)
        poll_1 = PollQuestion.objects.create(
            title="1-й день (начало дня)",
            message="Привет, Дивергент! Сегодня твой первый рабочий день. Ответь на несколько вопросов",
            days_after_hire=0,
            time_of_day="morning",
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=1,
        )

        list_questions = [
            ("Удалось ли тебе связаться с куратором?", "yes_no"),
            ("Ты знаешь, кто твой куратор?", "yes_no"),
            ("Сейчас с тобой свяжется наш менеджер и решит проблему", "finish"),
            ("Отлично, хорошего тебе рабочего дня - вечером я еще вернусь узнать, как твои дела", "finish"),
            ("Напиши пожалуйста своему куратору", "finish")
        ]

        questions = create_questions(poll_1, list_questions)

        list_conditions = [
            (questions[1], questions[0], "no"),
            (questions[2], questions[1], "no"),
            (questions[3], questions[0], "yes"),
            (questions[4], questions[1], "yes")
        ]

        create_conditions(list_conditions)

        poll_2 = PollQuestion.objects.create(
            title="1-й день (конец дня)",
            message="Подошел к концу твой первый рабочий день, ответь на несколько вопросов.",
            days_after_hire=0,
            time_of_day="evening",
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=2,
        )

        list_questions = [
            ("Сегодня завершился твой первый рабочий день. Как все прошло? Все ли было хорошо?", "yes_no"),
            ("Опиши, пожалуйста, подробнее", "message"),
            (
                "Спасибо за ответ! Мы постараемся решить описанные трудности. Завтра тебе напишет менеджер, чтобы узнать, как мы можем помочь",
                "finish"),
            ("Хорошего вечера!", "finish")
        ]

        questions = create_questions(poll_2, list_questions)

        list_conditions = [
            (questions[1], questions[0], "no"),
            (questions[3], questions[0], "yes"),
            (questions[2], questions[1], "some_text")]

        create_conditions(list_conditions)

        poll_3 = PollQuestion.objects.create(
            title="1-я неделя",
            message="Привет! Сегодня неделя, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
            days_after_hire=7,
            time_of_day="morning",
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=3,
        )

        list_questions = [
            ("Все ли необходимые доступы получены?", "yes_no"),
            ("Какие доступы еще не были предоставлены?", "message"),
            ("Спасибо! Мы передали информацию нашему менеджеру", "next"),
            ("Получен ли  подписанный договор от отдела кадров?", "yes_no"),
            ("Спасибо! Передали информацию в кадровый отдел", "next"),
            ("У тебя есть все необходимое для комфортной работы на проекте?", "yes_no"),
            ("Опиши, что именно тебе недостает для комфортной работы на проекте?", "message"),
            ("Спасибо! Мы постараемся решить эти вопросы", "next"),
            ("Знаешь ли ты расписание всех митингов и место их проведения?", "yes_no"),
            ("Спасибо! В скором времени тебя познакомят с расписанием необходимых встреч", "next"),
            (
                "Как бы ты оценил свой уровень удовлетворенности процессом онбординга? Поставь оценку от 1 до 5.",
                "numbers", EmployeeCategoryAnalytics.ONBOARDING_SATISFACTIONS),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо за обратную связь!", "finish")]

        questions = create_questions(poll_3, list_questions)

        list_conditions = [
            (questions[1], questions[0], "no"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[0], "yes"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "no"),
            (questions[5], questions[4], "next"),
            (questions[5], questions[3], "yes"),
            (questions[6], questions[5], "no"),
            (questions[7], questions[6], "some_text"),
            (questions[8], questions[5], "yes"),
            (questions[8], questions[7], "next"),
            (questions[9], questions[8], "no"),
            (questions[10], questions[9], "next"),
            (questions[10], questions[8], "yes"),
            (questions[11], questions[10], "1"),
            (questions[11], questions[10], "2"),
            (questions[11], questions[10], "3"),
            (questions[12], questions[10], "4"),
            (questions[12], questions[10], "5"),
            (questions[12], questions[11], "some_text")
        ]

        create_conditions(list_conditions)

        poll_4 = PollQuestion.objects.create(
            title="2-я неделя",
            message="Привет! Сегодня две недели, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
            days_after_hire=14,
            time_of_day="morning",
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=4,
        )

        list_questions = [
            ("Все ли необходимые доступы получены?", "yes_no"),
            ("Какие доступы еще не были предоставлены?", "message"),
            ("Спасибо! Мы передали информацию нашему менеджеру", "next"),
            ("Получен ли  подписанный договор от отдела кадров?", "yes_no"),
            ("Спасибо! Передали информацию в кадровый отдел", "next"),
            ("У тебя есть все необходимое для комфортной работы на проекте?", "yes_no"),
            ("Опиши, что именно тебе недостает для комфортной работы на проекте?", "message"),
            ("Спасибо! Мы постараемся решить эти вопросы", "next"),
            ("Знаешь ли ты расписание всех митингов и место их проведения?", "yes_no"),
            ("Спасибо! В скором времени тебя познакомят с расписанием необходимых встреч", "next"),
            (
                "Как бы ты оценил свой уровень удовлетворенности процессом онбординга? Поставь оценку от 1 до 5.",
                "numbers", EmployeeCategoryAnalytics.ONBOARDING_SATISFACTIONS),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты себя чувствуешь на проекте?", "numbers", EmployeeCategoryAnalytics.GENERAL_HEALTH),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо за обратную связь!", "finish")
        ]

        questions = create_questions(poll_4, list_questions)

        list_conditions = [
            (questions[1], questions[0], "no"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[0], "yes"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "no"),
            (questions[5], questions[4], "next"),
            (questions[5], questions[3], "yes"),
            (questions[6], questions[5], "no"),
            (questions[7], questions[6], "some_text"),
            (questions[8], questions[5], "yes"),
            (questions[8], questions[7], "next"),
            (questions[9], questions[8], "no"),
            (questions[10], questions[9], "next"),
            (questions[10], questions[8], "yes"),
            (questions[11], questions[10], "1"),
            (questions[11], questions[10], "2"),
            (questions[11], questions[10], "3"),
            (questions[12], questions[10], "4"),
            (questions[12], questions[10], "5"),
            (questions[12], questions[11], "some_text"),
            (questions[13], questions[12], "next"),
            (questions[14], questions[13], "1"),
            (questions[14], questions[13], "2"),
            (questions[14], questions[13], "3"),
            (questions[15], questions[13], "4"),
            (questions[15], questions[13], "5"),
            (questions[15], questions[14], "some_text"),
        ]

        create_conditions(list_conditions)

        poll_5 = PollQuestion.objects.create(
            title="1-й месяц",
            message="Привет! Сегодня месяц, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
            days_after_hire=30,
            time_of_day="morning",
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=5,
        )

        list_questions = [
            (
                "Насколько хорошо ты понимаешь свои обязанности и функционал? Поставь оценку от 1 до 5.",
                "numbers",
                EmployeeCategoryAnalytics.RESPONSIBILITIES),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты оцениваешь своё понимание задач и сроков их выполнения по шкале от 1 до 5?", "numbers",
             EmployeeCategoryAnalytics.UNDERSTAND_TASKS_DEADLINES),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Насколько твои ожидания соответствуют реальности? Оцени, пожалуйста, от 1 до 5.", "numbers",
             EmployeeCategoryAnalytics.JOB_EXPECTATIONS),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты оцениваешь атмосферу в нашей команде? Поставь, пожалуйста, оценку от 1 до 5.",
             "numbers",
             EmployeeCategoryAnalytics.TEAM_SATISFACTIONS),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты себя чувствуешь на проекте?", "numbers", EmployeeCategoryAnalytics.GENERAL_HEALTH),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next",),
            ("Какие изменения, на твой взгляд, могли бы помочь улучшить работу?", "message"),
            ("Спасибо за обратную связь!", "finish")
        ]

        questions = create_questions(poll_5, list_questions)

        list_conditions = [
            (questions[1], questions[0], "1"),
            (questions[1], questions[0], "2"),
            (questions[1], questions[0], "3"),
            (questions[2], questions[0], "4"),
            (questions[2], questions[0], "5"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "1"),
            (questions[4], questions[3], "2"),
            (questions[4], questions[3], "3"),
            (questions[5], questions[3], "4"),
            (questions[5], questions[3], "5"),
            (questions[5], questions[4], "some_text"),
            (questions[6], questions[5], "next"),
            (questions[7], questions[6], "1"),
            (questions[7], questions[6], "2"),
            (questions[7], questions[6], "3"),
            (questions[8], questions[6], "4"),
            (questions[8], questions[6], "5"),
            (questions[8], questions[7], "some_text"),
            (questions[9], questions[8], "next"),
            (questions[10], questions[9], "1"),
            (questions[10], questions[9], "2"),
            (questions[10], questions[9], "3"),
            (questions[11], questions[9], "4"),
            (questions[11], questions[9], "5"),
            (questions[11], questions[10], "some_text"),
            (questions[12], questions[11], "next"),
            (questions[13], questions[12], "1"),
            (questions[13], questions[12], "2"),
            (questions[13], questions[12], "3"),
            (questions[14], questions[12], "4"),
            (questions[14], questions[12], "5"),
            (questions[14], questions[13], "some_text"),
            (questions[15], questions[14], "next"),
            (questions[16], questions[15], "some_text"),
        ]

        create_conditions(list_conditions)

        poll_6 = PollQuestion.objects.create(
            title="2-й месяц",
            message="Привет! Скоро 2 месяца, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
            days_after_hire=50,
            time_of_day="morning",
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=6,
        )

        list_questions = [
            (
                "Насколько хорошо ты понимаешь свои обязанности и функционал? Поставь оценку от 1 до 5.",
                "numbers",
                EmployeeCategoryAnalytics.RESPONSIBILITIES),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты оцениваешь своё понимание задач и сроков их выполнения по шкале от 1 до 5?", "numbers",
             EmployeeCategoryAnalytics.UNDERSTAND_TASKS_DEADLINES),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message",),
            ("Спасибо!", "next"),
            ("Насколько твои ожидания соответствуют реальности? Оцени, пожалуйста, от 1 до 5.", "numbers",
             EmployeeCategoryAnalytics.JOB_EXPECTATIONS),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты оцениваешь атмосферу в нашей команде? Поставь, пожалуйста, оценку от 1 до 5.",
             "numbers",
             EmployeeCategoryAnalytics.TEAM_SATISFACTIONS),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты себя чувствуешь на проекте?", "numbers", EmployeeCategoryAnalytics.GENERAL_HEALTH),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Какие изменения, на твой взгляд, могли бы помочь улучшить работу?", "message"),
            ("Спасибо!", "next"),
            (
                "Видел ли ты встречу по окончанию ИС в календаре? Приглашение должно было прийти на твою почту.",
                "yes_no"),
            ("Спасибо за обратную связь!", "finish"),
            ("Сейчас с тобой свяжется менеджер и расскажет, когда будет встреча", "finish")
        ]

        questions = create_questions(poll_6, list_questions)

        list_conditions = [
            (questions[1], questions[0], "1"),
            (questions[1], questions[0], "2"),
            (questions[1], questions[0], "3"),
            (questions[2], questions[0], "4"),
            (questions[2], questions[0], "5"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "1"),
            (questions[4], questions[3], "2"),
            (questions[4], questions[3], "3"),
            (questions[5], questions[3], "4"),
            (questions[5], questions[3], "5"),
            (questions[5], questions[4], "some_text"),
            (questions[6], questions[5], "next"),
            (questions[7], questions[6], "1"),
            (questions[7], questions[6], "2"),
            (questions[7], questions[6], "3"),
            (questions[8], questions[6], "4"),
            (questions[8], questions[6], "5"),
            (questions[8], questions[7], "some_text"),
            (questions[9], questions[8], "next"),
            (questions[10], questions[9], "1"),
            (questions[10], questions[9], "2"),
            (questions[10], questions[9], "3"),
            (questions[11], questions[9], "4"),
            (questions[11], questions[9], "5"),
            (questions[11], questions[10], "some_text"),
            (questions[12], questions[11], "next"),
            (questions[13], questions[12], "1"),
            (questions[13], questions[12], "2"),
            (questions[13], questions[12], "3"),
            (questions[14], questions[12], "4"),
            (questions[14], questions[12], "5"),
            (questions[14], questions[13], "some_text"),
            (questions[15], questions[14], "next"),
            (questions[16], questions[15], "some_text"),
            (questions[17], questions[16], "next"),
            (questions[18], questions[17], "yes"),
            (questions[19], questions[17], "no"),
        ]

        create_conditions(list_conditions)

        poll_7 = PollQuestion.objects.create(
            title="3-й месяц",
            message="Привет! Сегодня 3 месяца, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
            days_after_hire=90,
            time_of_day="morning",
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=7,
        )

        list_questions = [
            (
                "Насколько хорошо ты понимаешь свои обязанности и функционал? Поставь оценку от 1 до 5.",
                "numbers",
                EmployeeCategoryAnalytics.RESPONSIBILITIES),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты оцениваешь своё понимание задач и сроков их выполнения по шкале от 1 до 5?", "numbers",
             EmployeeCategoryAnalytics.UNDERSTAND_TASKS_DEADLINES),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Насколько твои ожидания соответствуют реальности? Оцени, пожалуйста, от 1 до 5.", "numbers",
             EmployeeCategoryAnalytics.JOB_EXPECTATIONS),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты оцениваешь атмосферу в нашей команде? Поставь, пожалуйста, оценку от 1 до 5.",
             "numbers",
             EmployeeCategoryAnalytics.TEAM_SATISFACTIONS),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Как ты себя чувствуешь на проекте?", "numbers", EmployeeCategoryAnalytics.GENERAL_HEALTH),
            ("Можешь объяснить, что именно повлияло на твою оценку?", "message"),
            ("Спасибо!", "next"),
            ("Какие изменения, на твой взгляд, могли бы помочь улучшить работу?", "message"),
            ("Спасибо за обратную связь!", "finish")
        ]

        questions = create_questions(poll_7, list_questions)

        list_conditions = [
            (questions[1], questions[0], "1"),
            (questions[1], questions[0], "2"),
            (questions[1], questions[0], "3"),
            (questions[2], questions[0], "4"),
            (questions[2], questions[0], "5"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "1"),
            (questions[4], questions[3], "2"),
            (questions[4], questions[3], "3"),
            (questions[5], questions[3], "4"),
            (questions[5], questions[3], "5"),
            (questions[5], questions[4], "some_text"),
            (questions[6], questions[5], "next"),
            (questions[7], questions[6], "1"),
            (questions[7], questions[6], "2"),
            (questions[7], questions[6], "3"),
            (questions[8], questions[6], "4"),
            (questions[8], questions[6], "5"),
            (questions[8], questions[7], "some_text"),
            (questions[9], questions[8], "next"),
            (questions[10], questions[9], "1"),
            (questions[10], questions[9], "2"),
            (questions[10], questions[9], "3"),
            (questions[11], questions[9], "4"),
            (questions[11], questions[9], "5"),
            (questions[11], questions[10], "some_text"),
            (questions[12], questions[11], "next"),
            (questions[13], questions[12], "1"),
            (questions[13], questions[12], "2"),
            (questions[13], questions[12], "3"),
            (questions[14], questions[12], "4"),
            (questions[14], questions[12], "5"),
            (questions[14], questions[13], "some_text"),
            (questions[15], questions[14], "next"),
            (questions[16], questions[15], "some_text"),
        ]

        create_conditions(list_conditions)

        poll_8 = PollQuestion.objects.create(
            title="1-й день",
            message="Сегодня первый рабочий день сотрудника {}. Ответьте, пожалуйста, на несколько вопросов",
            days_after_hire=0,
            time_of_day="morning",
            intended_for=UserType.CURATOR,
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=1,
        )

        list_questions = [
            ("Удалось ли связаться с ним?", "yes_no"),
            ("Спасибо! Информацию передали менеджеру", "finish"),
        ]

        questions = create_questions(poll_8, list_questions)

        list_conditions = [
            (questions[1], questions[0], "yes"),
            (questions[1], questions[0], "no"),
        ]

        create_conditions(list_conditions)

        poll_9 = PollQuestion.objects.create(
            title="1-я неделя",
            message="Здравствуйте! Сегодня неделя, как с Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
            days_after_hire=7,
            time_of_day="morning",
            intended_for=UserType.CURATOR,
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=2,
        )

        list_questions = [
            ("Удалось ли настроить рабочее место и необходимые доступы сотруднику?", "yes_no"),
            ("Напишите, какие доступы необходимо настроить", "message"),
            ("Спасибо! Информацию передали менеджеру!", "next"),
            ("Насколько Вы удовлетворены тем, как втягивается в работу сотрудник?", "numbers",
             CuratorCategoryAnalytics.INVOLVEMENT),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Сотрудник вовремя выходит на связь?", "yes_no"),
            ("Сотрудник присутствует на встречах?", "yes_no"),
            ("Спасибо за обратную связь!", "finish"),
        ]

        questions = create_questions(poll_9, list_questions)

        list_conditions = [
            (questions[1], questions[0], "no"),
            (questions[3], questions[0], "yes"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "1"),
            (questions[4], questions[3], "2"),
            (questions[4], questions[3], "3"),
            (questions[6], questions[3], "4"),
            (questions[6], questions[3], "5"),
            (questions[5], questions[4], "some_text"),
            (questions[6], questions[5], "next"),
            (questions[7], questions[6], "yes"),
            (questions[7], questions[6], "no"),
            (questions[8], questions[7], "yes"),
            (questions[8], questions[7], "no"),
        ]

        create_conditions(list_conditions)

        poll_10 = PollQuestion.objects.create(
            title="1-й месяц",
            message="Здравствуйте! Сегодня месяц, как с Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
            days_after_hire=30,
            time_of_day="morning",
            intended_for=UserType.CURATOR,
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=3,
        )

        list_questions = [
            ("Оцените, насколько вы удовлетворены качеством выполнения сотрудником своих задач?", "numbers",
             CuratorCategoryAnalytics.QUALITY_TASKS),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Оцените, насколько вы удовлетворены уровнем дисциплины сотрудника", "numbers",
             CuratorCategoryAnalytics.DISCIPLINE),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Оцените, насколько вы удовлетворены качеством взаимодействия сотрудника с командой?",
             "numbers",
             CuratorCategoryAnalytics.QUALITY_INTERACTIONS),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Сотрудник полностью соответствует ожиданиям?", "yes_no"),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Все ли доступы удалось выдать сотруднику?", "yes_no"),
            ("Напишите, какие доступы еще не выдали", "message"),
            ("Сотрудник вовремя выходит на связь?", "yes_no"),
            ("Сотрудник присутствует на встречах?", "yes_no"),
            ("Оставляем сотрудника?", "yes_no"),
            ("Почему вы дали такой ответ?", "message"),
            ("Спасибо за обратную связь!", "finish")
        ]

        questions = create_questions(poll_10, list_questions)

        list_conditions = [
            (questions[1], questions[0], "1"),
            (questions[1], questions[0], "2"),
            (questions[1], questions[0], "3"),
            (questions[3], questions[0], "4"),
            (questions[3], questions[0], "5"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "1"),
            (questions[4], questions[3], "2"),
            (questions[4], questions[3], "3"),
            (questions[6], questions[3], "4"),
            (questions[6], questions[3], "5"),
            (questions[5], questions[4], "some_text"),
            (questions[6], questions[5], "next"),
            (questions[7], questions[6], "1"),
            (questions[7], questions[6], "2"),
            (questions[7], questions[6], "3"),
            (questions[9], questions[6], "4"),
            (questions[9], questions[6], "5"),
            (questions[8], questions[7], "some_text"),
            (questions[9], questions[8], "next"),
            (questions[10], questions[9], "no"),
            (questions[11], questions[9], "yes"),
            (questions[11], questions[10], "some_text"),
            (questions[12], questions[11], "no"),
            (questions[13], questions[11], "yes"),
            (questions[13], questions[12], "some_text"),
            (questions[14], questions[13], "no"),
            (questions[14], questions[13], "yes"),
            (questions[15], questions[14], "no"),
            (questions[15], questions[14], "yes"),
            (questions[16], questions[15], "no"),
            (questions[17], questions[15], "yes"),
            (questions[17], questions[16], "some_text")
        ]

        create_conditions(list_conditions)

        poll_11 = PollQuestion.objects.create(
            title="2-й месяц",
            message="Здравствуйте! Скоро два месяца, как с Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
            days_after_hire=50,
            time_of_day="morning",
            intended_for=UserType.CURATOR,
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=4,
        )

        list_questions = [
            ("Оцените, насколько вы удовлетворены качеством выполнения сотрудником своих задач?", "numbers",
             CuratorCategoryAnalytics.QUALITY_TASKS),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Оцените, насколько вы удовлетворены уровнем дисциплины сотрудника", "numbers",
             CuratorCategoryAnalytics.DISCIPLINE),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Оцените, насколько вы удовлетворены качеством взаимодействия сотрудника с командой?",
             "numbers",
             CuratorCategoryAnalytics.QUALITY_INTERACTIONS),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Сотрудник полностью соответствует ожиданиям?", "yes_no"),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Все ли доступы удалось выдать сотруднику?", "yes_no"),
            ("Напишите, какие доступы еще не выдали", "message"),
            ("Сотрудник вовремя выходит на связь?", "yes_no"),
            ("Сотрудник присутствует на встречах?", "yes_no"),
            ("Оставляем сотрудника?", "yes_no"),
            ("Почему вы дали такой ответ?", "message"),
            ("Спасибо за обратную связь!", "finish")
        ]

        questions = create_questions(poll_11, list_questions)

        list_conditions = [
            (questions[1], questions[0], "1"),
            (questions[1], questions[0], "2"),
            (questions[1], questions[0], "3"),
            (questions[3], questions[0], "4"),
            (questions[3], questions[0], "5"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "1"),
            (questions[4], questions[3], "2"),
            (questions[4], questions[3], "3"),
            (questions[6], questions[3], "4"),
            (questions[6], questions[3], "5"),
            (questions[5], questions[4], "some_text"),
            (questions[6], questions[5], "next"),
            (questions[7], questions[6], "1"),
            (questions[7], questions[6], "2"),
            (questions[7], questions[6], "3"),
            (questions[9], questions[6], "4"),
            (questions[9], questions[6], "5"),
            (questions[8], questions[7], "some_text"),
            (questions[9], questions[8], "next"),
            (questions[10], questions[9], "no"),
            (questions[11], questions[9], "yes"),
            (questions[11], questions[10], "some_text"),
            (questions[12], questions[11], "no"),
            (questions[13], questions[11], "yes"),
            (questions[13], questions[12], "some_text"),
            (questions[14], questions[13], "no"),
            (questions[14], questions[13], "yes"),
            (questions[15], questions[14], "no"),
            (questions[15], questions[14], "yes"),
            (questions[16], questions[15], "no"),
            (questions[17], questions[15], "yes"),
            (questions[17], questions[16], "some_text")
        ]

        create_conditions(list_conditions)

        poll_12 = PollQuestion.objects.create(
            title="3-й месяц",
            message="Здравствуйте! Сегодня три месяца, как с Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
            days_after_hire=90,
            time_of_day="morning",
            intended_for=UserType.CURATOR,
            content_type=project_content_type,
            object_id=instance.id,
            poll_number=5,
        )

        list_questions = [
            ("Оцените, насколько вы удовлетворены качеством выполнения сотрудником своих задач?", "numbers",
             CuratorCategoryAnalytics.QUALITY_TASKS),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Оцените, насколько вы удовлетворены уровнем дисциплины сотрудника", "numbers",
             CuratorCategoryAnalytics.DISCIPLINE),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Оцените, насколько вы удовлетворены качеством взаимодействия сотрудника с командой?",
             "numbers",
             CuratorCategoryAnalytics.QUALITY_INTERACTIONS),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Спасибо! Информацию передали менеджеру", "next"),
            ("Сотрудник полностью соответствует ожиданиям?", "yes_no"),
            ("Почему вы дали такой ответ на этот вопрос?", "message"),
            ("Все ли доступы удалось выдать сотруднику?", "yes_no"),
            ("Напишите, какие доступы еще не выдали", "message"),
            ("Сотрудник вовремя выходит на связь?", "yes_no"),
            ("Сотрудник присутствует на встречах?", "yes_no"),
            ("Оставляем сотрудника?", "yes_no"),
            ("Почему вы дали такой ответ?", "message"),
            ("Спасибо за обратную связь!", "finish")
        ]

        questions = create_questions(poll_12, list_questions)

        list_conditions = [
            (questions[1], questions[0], "1"),
            (questions[1], questions[0], "2"),
            (questions[1], questions[0], "3"),
            (questions[3], questions[0], "4"),
            (questions[3], questions[0], "5"),
            (questions[2], questions[1], "some_text"),
            (questions[3], questions[2], "next"),
            (questions[4], questions[3], "1"),
            (questions[4], questions[3], "2"),
            (questions[4], questions[3], "3"),
            (questions[6], questions[3], "4"),
            (questions[6], questions[3], "5"),
            (questions[5], questions[4], "some_text"),
            (questions[6], questions[5], "next"),
            (questions[7], questions[6], "1"),
            (questions[7], questions[6], "2"),
            (questions[7], questions[6], "3"),
            (questions[9], questions[6], "4"),
            (questions[9], questions[6], "5"),
            (questions[8], questions[7], "some_text"),
            (questions[9], questions[8], "next"),
            (questions[10], questions[9], "no"),
            (questions[11], questions[9], "yes"),
            (questions[11], questions[10], "some_text"),
            (questions[12], questions[11], "no"),
            (questions[13], questions[11], "yes"),
            (questions[13], questions[12], "some_text"),
            (questions[14], questions[13], "no"),
            (questions[14], questions[13], "yes"),
            (questions[15], questions[14], "no"),
            (questions[15], questions[14], "yes"),
            (questions[16], questions[15], "no"),
            (questions[17], questions[15], "yes"),
            (questions[17], questions[16], "some_text")
        ]

        create_conditions(list_conditions)
