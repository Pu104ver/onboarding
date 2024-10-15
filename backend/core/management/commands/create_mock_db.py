from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from projects.models import Project
from questions.utils import create_questions, create_conditions
from questions.models import (
    PollQuestion,
    KeyboardType,
    UserType,
    PollType, 
    EmployeeCategoryAnalytics, 
    CuratorCategoryAnalytics,
)
from slots.models import Slot


class Command(BaseCommand):
    help = "Создать опросы обратной связи и оффбординга, слоты, клавиатуру в БД и опросы к проектам"

    def handle(self, *args, **kwargs):

        try:
            with transaction.atomic():

                old_poll_questions = PollQuestion.objects.all()
                old_poll_questions.delete()

                poll_1 = PollQuestion.objects.create(
                    title="6-й месяц",
                    message="Привет! Сегодня 6 месяцев, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
                    days_after_hire=180,
                    time_of_day="morning",
                    poll_type=PollType.FEEDBACK,
                    poll_number=1,
                )

                list_questions = [
                    (
                        "Насколько интересен проект, над которым ты работаешь, и задачи, которые выполняешь? Оцени от 1 до 5.",
                        "numbers", EmployeeCategoryAnalytics.INTEREST_PROJECT),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Как ты оцениваешь качество обратной связи от руководителя? Поставь оценку от 1 до 5.", "numbers",
                     EmployeeCategoryAnalytics.QUALITY_FEEDBACK),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Насколько совпадают задачи с твоими ожиданиями? Оцени от 1 до 5.", "numbers",
                     EmployeeCategoryAnalytics.PROJECT_EXPECTATIONS),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message",),
                    ("Спасибо!", "next"),
                    ("Все ли идет гладко при выполнении задач, взаимодействии с командой и получении доступов?",
                     "yes_no"),
                    ("Опиши, пожалуйста, в чем заключается сложность?", "message"),
                    ("Спасибо!", "next"),
                    ("Как ты себя чувствуешь на проекте?", "numbers", EmployeeCategoryAnalytics.GENERAL_HEALTH),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Что бы ты предложил улучшить?", "message"),
                    ("Спасибо!", "finish"),
                ]

                questions = create_questions(poll_1, list_questions)

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
                    (questions[10], questions[9], "no"),
                    (questions[11], questions[10], "some_text"),
                    (questions[11], questions[9], "yes"),
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

                poll_2 = PollQuestion.objects.create(
                    title="9-й месяц",
                    message="Привет! Сегодня 9 месяцев, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
                    days_after_hire=270,
                    time_of_day="morning",
                    poll_type=PollType.FEEDBACK,
                    poll_number=2,
                )

                list_questions = [
                    (
                    "Насколько интересен проект, над которым ты работаешь, и задачи, которые выполняешь? Оцени от 1 до 5.",
                    "numbers", EmployeeCategoryAnalytics.INTEREST_PROJECT),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Как ты оцениваешь качество обратной связи от руководителя? Поставь оценку от 1 до 5.", "numbers",
                     EmployeeCategoryAnalytics.QUALITY_FEEDBACK),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Насколько совпадают задачи с твоими ожиданиями? Оцени от 1 до 5.", "numbers",
                     EmployeeCategoryAnalytics.PROJECT_EXPECTATIONS),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message",),
                    ("Спасибо!", "next"),
                    ("Все ли идет гладко при выполнении задач, взаимодействии с командой и получении доступов?",
                     "yes_no"),
                    ("Опиши, пожалуйста, в чем заключается сложность?", "message"),
                    ("Спасибо!", "next"),
                    ("Как ты себя чувствуешь на проекте?", "numbers", EmployeeCategoryAnalytics.GENERAL_HEALTH),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Что бы ты предложил улучшить?", "message"),
                    ("Спасибо!", "finish"),
                ]

                questions = create_questions(poll_2, list_questions)

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
                    (questions[10], questions[9], "no"),
                    (questions[11], questions[10], "some_text"),
                    (questions[11], questions[9], "yes"),
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

                poll_3 = PollQuestion.objects.create(
                    title="12-й месяц",
                    message="Привет! Сегодня 12 месяцев, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
                    days_after_hire=360,
                    time_of_day="morning",
                    poll_type=PollType.FEEDBACK,
                    poll_number=3,
                )

                list_questions = [
                    (
                        "Насколько интересен проект, над которым ты работаешь, и задачи, которые выполняешь? Оцени от 1 до 5.",
                        "numbers", EmployeeCategoryAnalytics.INTEREST_PROJECT),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Как ты оцениваешь качество обратной связи от руководителя? Поставь оценку от 1 до 5.", "numbers",
                     EmployeeCategoryAnalytics.QUALITY_FEEDBACK),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Насколько совпадают задачи с твоими ожиданиями? Оцени от 1 до 5.", "numbers",
                     EmployeeCategoryAnalytics.PROJECT_EXPECTATIONS),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message",),
                    ("Спасибо!", "next"),
                    ("Все ли идет гладко при выполнении задач, взаимодействии с командой и получении доступов?",
                     "yes_no"),
                    ("Опиши, пожалуйста, в чем заключается сложность?", "message"),
                    ("Спасибо!", "next"),
                    ("Как ты себя чувствуешь на проекте?", "numbers", EmployeeCategoryAnalytics.GENERAL_HEALTH),
                    ("Подскажи, пожалуйста, почему ты поставил такую оценку?", "message"),
                    ("Спасибо!", "next"),
                    ("Что бы ты предложил улучшить?", "message"),
                    ("Спасибо!", "finish"),
                ]

                questions = create_questions(poll_3, list_questions)

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
                    (questions[10], questions[9], "no"),
                    (questions[11], questions[10], "some_text"),
                    (questions[11], questions[9], "yes"),
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

                poll_4 = PollQuestion.objects.create(
                    title="6-й месяц",
                    message="Здравствуйте! c Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
                    days_after_hire=180,
                    time_of_day="morning",
                    intended_for=UserType.CURATOR,
                    poll_type=PollType.FEEDBACK,
                    poll_number=1,
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
                    ("Оцените, насколько вы удовлетворены качеством взаимодействия сотрудника с командой?", "numbers",
                     CuratorCategoryAnalytics.QUALITY_INTERACTIONS),
                    ("Почему вы дали такой ответ на этот вопрос?", "message"),
                    ("Спасибо! Информацию передали менеджеру", "next"),
                    ("Сотрудник полностью соответствует ожиданиям?", "yes_no"),
                    ("Почему вы дали такой ответ на этот вопрос?", "message"),
                    ("Сотрудник вовремя выходит на связь?", "yes_no"),
                    ("Сотрудник присутствует на встречах?", "yes_no"),
                    ("Спасибо за обратную связь!", "finish")
                ]

                questions = create_questions(poll_4, list_questions)

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
                    (questions[11], questions[9], "yes"),
                    (questions[10], questions[9], "no"),
                    (questions[11], questions[10], "some_text"),
                    (questions[12], questions[11], "yes"),
                    (questions[12], questions[11], "no"),
                    (questions[13], questions[12], "yes"),
                    (questions[13], questions[12], "no"),
                ]

                create_conditions(list_conditions)

                poll_5 = PollQuestion.objects.create(
                    title="Последний рабочий день",
                    message="Привет! Сегодня твой последний рабочий день. Мы надеемся, что за время нашего сотрудничества ты получил полезный и уникальный опыт! Ответь, пожалуйста, на организационные вопросы",
                    poll_type=PollType.OFFBOARDING,
                    poll_number=1,
                )

                list_questions = [
                    ("Проинформировал(а) команду об уходе?", "yes_no"),
                    ("Все ли доступы ты закрыл(а)?", "yes_no"),
                    ("Передал(а) ли ты оставшииеся дела/задачи?", "yes_no"),
                    ("Получил(а) расчетный лист?", "yes_no"),
                    (
                        "Спасибо за ответы! Мы хотели бы узнать у тебя, все ли тебя устраивало во время работы с нами. Поэтому приглашаем тебя на выходное интервью: Выбери время, когда тебе было бы удобно созвониться (около 15-20 минут)",
                        "slots",),
                    ("Спасибо! За 30 минут с тобой свяжется наш менеджер. Успехов тебе на твоем профессиональном пути!",
                     "finish"),
                ]

                questions = create_questions(poll_5, list_questions)

                list_conditions = [
                    (questions[1], questions[0], "yes"),
                    (questions[1], questions[0], "no"),
                    (questions[2], questions[1], "yes"),
                    (questions[2], questions[1], "no"),
                    (questions[3], questions[2], "yes"),
                    (questions[3], questions[2], "no"),
                    (questions[4], questions[3], "yes"),
                    (questions[4], questions[3], "no"),
                    (questions[5], questions[4], "slots"),
                ]

                create_conditions(list_conditions)

                poll_6 = PollQuestion.objects.create(
                    title="9-й месяц",
                    message="Здравствуйте! c Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
                    days_after_hire=270,
                    time_of_day="morning",
                    intended_for=UserType.CURATOR,
                    poll_type=PollType.FEEDBACK,
                    poll_number=2,
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
                    ("Оцените, насколько вы удовлетворены качеством взаимодействия сотрудника с командой?", "numbers",
                     CuratorCategoryAnalytics.QUALITY_INTERACTIONS),
                    ("Почему вы дали такой ответ на этот вопрос?", "message"),
                    ("Спасибо! Информацию передали менеджеру", "next"),
                    ("Сотрудник полностью соответствует ожиданиям?", "yes_no"),
                    ("Почему вы дали такой ответ на этот вопрос?", "message"),
                    ("Сотрудник вовремя выходит на связь?", "yes_no"),
                    ("Сотрудник присутствует на встречах?", "yes_no"),
                    ("Спасибо за обратную связь!", "finish")
                ]

                questions = create_questions(poll_6, list_questions)

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
                    (questions[11], questions[9], "yes"),
                    (questions[10], questions[9], "no"),
                    (questions[11], questions[10], "some_text"),
                    (questions[12], questions[11], "yes"),
                    (questions[12], questions[11], "no"),
                    (questions[13], questions[12], "yes"),
                    (questions[13], questions[12], "no"),
                ]

                create_conditions(list_conditions)

                poll_7 = PollQuestion.objects.create(
                    title="12-й месяц",
                    message="Здравствуйте! c Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
                    days_after_hire=360,
                    time_of_day="morning",
                    intended_for=UserType.CURATOR,
                    poll_type=PollType.FEEDBACK,
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
                    ("Оцените, насколько вы удовлетворены качеством взаимодействия сотрудника с командой?", "numbers",
                     CuratorCategoryAnalytics.QUALITY_INTERACTIONS),
                    ("Почему вы дали такой ответ на этот вопрос?", "message"),
                    ("Спасибо! Информацию передали менеджеру", "next"),
                    ("Сотрудник полностью соответствует ожиданиям?", "yes_no"),
                    ("Почему вы дали такой ответ на этот вопрос?", "message"),
                    ("Сотрудник вовремя выходит на связь?", "yes_no"),
                    ("Сотрудник присутствует на встречах?", "yes_no"),
                    ("Спасибо за обратную связь!", "finish")
                ]

                questions = create_questions(poll_7, list_questions)

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
                    (questions[11], questions[9], "yes"),
                    (questions[10], questions[9], "no"),
                    (questions[11], questions[10], "some_text"),
                    (questions[12], questions[11], "yes"),
                    (questions[12], questions[11], "no"),
                    (questions[13], questions[12], "yes"),
                    (questions[13], questions[12], "no"),
                ]

                create_conditions(list_conditions)

                project_content_type = ContentType.objects.get_for_model(Project)

                projects = Project.objects.all()
                for instance in projects:
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

                poll_13 = PollQuestion.objects.create(
                    title="4-й месяц",
                    message="Привет! Сегодня 4 месяца, как ты работаешь с нами) Ответь, пожалуйста на несколько вопросов.",
                    days_after_hire=120,
                    time_of_day="morning",
                    intended_for=UserType.EMPLOYEE,
                    poll_number=1,
                    poll_type=PollType.INTERMEDIATE_FEEDBACK,
                )

                list_questions = [
                    ("Ты регулярно выходишь на связь?", "yes_no"),
                    ("Ты посещаешь все встречи?", "yes_no"),
                    ("Ты предупреждаешь об отсутствиях заранее?", "yes_no"),
                    ("Ты включаешь камеру на встречах?", "yes_no"),
                    ("Все ли соответствует твоим ожиданиям?", "yes_no"),
                    ("Напиши свои вопросы или комментарии", "message"),
                    ("Спасибо за обратную связь!", "finish")
                ]

                questions = create_questions(poll_13, list_questions)

                list_conditions = [
                    (questions[1], questions[0], "yes"),
                    (questions[1], questions[0], "no"),
                    (questions[2], questions[1], "yes"),
                    (questions[2], questions[1], "no"),
                    (questions[3], questions[2], "yes"),
                    (questions[3], questions[2], "no"),
                    (questions[4], questions[3], "yes"),
                    (questions[4], questions[3], "no"),
                    (questions[5], questions[4], "no"),
                    (questions[6], questions[4], "yes"),
                    (questions[6], questions[5], "some_text"),
                ]

                create_conditions(list_conditions)

                poll_13 = PollQuestion.objects.create(
                    title="4-й месяц",
                    message="Здравствуйте! c Вами работает {}. Ответьте, пожалуйста, на несколько вопросов",
                    days_after_hire=120,
                    time_of_day="morning",
                    intended_for=UserType.CURATOR,
                    poll_number=1,
                    poll_type=PollType.INTERMEDIATE_FEEDBACK,
                )

                list_questions = [
                    ("Сотрудник регулярно выходит на связь?", "yes_no"),
                    ("Сотрудник посещает все встречи?", "yes_no"),
                    ("Сотрудник предупреждает об отсутствиях заранее?", "yes_no"),
                    ("Сотрудник включает камеру на встречах?", "yes_no"),
                    ("Сотрудник полностью соответствует ожиданиям?", "yes_no"),
                    ("Напишите свои вопросы или комментарии", "message"),
                    ("Спасибо за обратную связь!", "finish")
                ]

                questions = create_questions(poll_13, list_questions)

                list_conditions = [
                    (questions[1], questions[0], "yes"),
                    (questions[1], questions[0], "no"),
                    (questions[2], questions[1], "yes"),
                    (questions[2], questions[1], "no"),
                    (questions[3], questions[2], "yes"),
                    (questions[3], questions[2], "no"),
                    (questions[4], questions[3], "yes"),
                    (questions[4], questions[3], "no"),
                    (questions[5], questions[4], "no"),
                    (questions[6], questions[4], "yes"),
                    (questions[6], questions[5], "some_text"),
                ]

                create_conditions(list_conditions)

                KeyboardType.objects.get_or_create(
                    question_type="yes_no",
                    keyboard_json={
                        "inline_keyboard": [
                            {"text": "Да", "callback_data": "yes"},
                            {"text": "Нет", "callback_data": "no"},
                        ]
                    },
                )
                KeyboardType.objects.get_or_create(
                    question_type="numbers",
                    keyboard_json={
                        "inline_keyboard": [
                            {"text": "1", "callback_data": "1"},
                            {"text": "2", "callback_data": "2"},
                            {"text": "3", "callback_data": "3"},
                            {"text": "4", "callback_data": "4"},
                            {"text": "5", "callback_data": "5"},
                        ]
                    },
                )
                KeyboardType.objects.get_or_create(
                    question_type="next",
                    keyboard_json={
                        "inline_keyboard": [{"text": "Далее", "callback_data": "next"}]
                    },
                )

                today = timezone.now().date()
                Slot.objects.get_or_create(start_time="15:00", date=today)
                Slot.objects.get_or_create(start_time="16:00", date=today)
                Slot.objects.get_or_create(start_time="17:00", date=today)
                Slot.objects.get_or_create(start_time="18:00", date=today)

                self.stdout.write(self.style.SUCCESS("Success"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка при создании данных: {e}"))
