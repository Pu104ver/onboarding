from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from questions.services import PollsService
from questions.models import (
    PollQuestion,
    PollStatus,
    UserAnswer,
    Question,
    QuestionType,
)
from employees.models import Employee
from questions.models import UserAnswer, PollType
from api.serializers.questions import (
    PlannedPollsListSerializer,
    PollQuestionSerializer,
    UserAnswerSerializer,
    PollStatusSkipSerializer,
    PollStatusSerializer,
    CreatePollSerializer,
    UserAnswerExportSerializer,
)
from api.filters.questions import (
    PlannedPollsListFilter,
    UserAnswerFilter,
    AvailablePollQuestionsFilter,
)
from django.db.models import (
    Case,
    When,
    Value,
    IntegerField,
)
from django.db import transaction
from django.shortcuts import get_object_or_404


class AvailablePollQuestionsView(generics.ListAPIView):
    serializer_class = PollQuestionSerializer
    filterset_class = AvailablePollQuestionsFilter
    permission_classes = [IsAuthenticated]
    queryset = (
        PollQuestion.objects.exclude(poll_type=PollType.INTERMEDIATE_FEEDBACK)
        .order_by("poll_number")
        .select_related("content_type")
    )


class PlannedPollsListView(generics.ListAPIView):
    """
    API для получения списка запланированных опросов.

    Возвращает подробный список опросов в JSON-формате.
    """

    serializer_class = PlannedPollsListSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PlannedPollsListFilter

    def get_queryset(self):
        """
        Сортирует опросы по дате завершения, чтобы "вверху" были опросы с наиболее поздней датой, а пустые (isnull) упали "вниз".
        """

        queryset = (
            PollStatus.objects.all().order_by(
                Case(
                    When(completed_at__isnull=True, then=Value(1)),
                    When(completed_at__isnull=False, then=Value(0)),
                    output_field=IntegerField(),
                ),
                "-completed_at",
            )
        ).select_related("poll", "employee", "target_employee")

        return queryset

    def get_serializer_context(self):
        """
        Добавляет в контекст сотрудника и таргета, нужно для фильтрации вопросов в to_representation сериализатора.
        """
        context = super().get_serializer_context()
        # при желании можно еще добавить параметров для фильтрации и они автоматически будут применены в сериализаторе (да, я запихал задел под масштабирование, там где он в принципе не нужен, и что вы мне сделаете? хехе)
        filter_params = {
            "employee": int,
            "target_employee": int,
        }
        for param, param_type in filter_params.items():
            value = self.request.query_params.get(param)
            if value:
                try:
                    context[param] = param_type(value)
                except ValueError:
                    # не знаю стоит ли такую ошибку возвращать в апишку, так что пусть пока будет так
                    # raise ValidationError("Передан недопустимый тип параметра")
                    continue

        return context


class CreatePollView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatePollSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        employee: Employee = data.get("employee")
        target_employee: Employee = data.get("target_employee", None)
        poll: PollQuestion = data.get("poll")
        date_planned_at = data.get("date_planned_at")

        with transaction.atomic():
            poll_status, error = PollsService.create_poll(
                employee, poll, date_planned_at, target_employee=target_employee
            )
            if error:
                raise ValidationError(error)

            return Response(
                PollStatusSerializer(poll_status).data,
                status=status.HTTP_201_CREATED,
            )


class EmployeePollsWithAnswersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, employee_id):
        user_answers = UserAnswer.objects.filter(employee_id=employee_id)
        poll_ids = user_answers.values_list("question__poll_id", flat=True).distinct()
        polls = PollStatus.objects.filter(poll__id__in=poll_ids)
        serializer = PollStatusSerializer(polls, many=True)

        return Response(serializer.data)


class PollStatusTypesListView(APIView):
    """
    API для получения всех типов статусов опроса.

    Возвращает список статусов опроса в JSON-формате.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        statuses = [
            {"value": status.value, "display_name": status.label}
            for status in PollStatus.Status
        ]
        return Response(statuses, status=status.HTTP_200_OK)


class UserAnswerListView(generics.ListAPIView):
    """
    API для получения списка ответов пользователя.

    Возвращает список ответов пользователя в JSON-формате.
    """

    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = UserAnswerFilter


class CompletePollStatusView(APIView):
    """
    API для завершения опроса.

    Возвращает данные завершенного опроса.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, poll_status_id):
        poll_status = get_object_or_404(PollStatus, id=poll_status_id)
        serializer = PollStatusSkipSerializer(
            poll_status, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExportAnswersView(generics.GenericAPIView):
    queryset = (
        UserAnswer.objects.exclude(question__question_type=QuestionType.NEXT)
        .select_related("employee", "target_employee", "question", "question__poll")
        .prefetch_related("employee__employee_pollstatus")
        .distinct()
        .order_by("id")
    )
    permission_classes = [IsAuthenticated]
    serializer_class = UserAnswerExportSerializer

    def post(self, request: Request):
        try:
            serializer: UserAnswerExportSerializer = self.get_serializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data

            employee_list: list[Employee] = validated_data.get("employee", [])
            target_employee_list: list[Employee] = validated_data.get(
                "target_employee", []
            )
            question_list: list[Question] = validated_data.get("question", [])
            poll_list: list[PollQuestion] = validated_data.get("poll", [])
            poll_status: str = validated_data.get("poll_status")
            file_format: str = validated_data.get("file_format", "xlsx")

            answers, error = PollsService.filter_users_answers(
                employees_ids=employee_list,
                target_employees_ids=target_employee_list,
                questions_ids=question_list,
                polls_ids=poll_list,
                poll_status=poll_status,
                answers=self.get_queryset(),
            )

            if error:
                raise ValidationError(error)

            # в сериализаторе убрал возможность выбора csv до моменты решения проблемы
            if file_format == "csv":
                file, error = PollsService.generate_csv(answers)
            elif file_format == "xlsx":
                file, error = PollsService.generate_excel(answers)
            if error:
                raise ValidationError(error)
            return file

        except Exception as e:
            return self.handle_exception(e)
