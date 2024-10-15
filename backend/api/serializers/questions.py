from rest_framework import serializers
from questions.models import (
    PollQuestion,
    Question,
    UserAnswer,
    PollStatus,
)
from employees.models import Employee
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType


class UserAnswerSerializer(serializers.ModelSerializer):
    employee = serializers.StringRelatedField()
    target_employee = serializers.StringRelatedField()
    employee_id = serializers.PrimaryKeyRelatedField(
        source="employee", read_only=True, write_only=False
    )
    target_employee_id = serializers.PrimaryKeyRelatedField(
        source="target_employee", read_only=True, write_only=False
    )
    question_title = serializers.CharField(source="question.text", read_only=True)
    poll_id = serializers.PrimaryKeyRelatedField(
        source="question.poll.id", read_only=True
    )
    poll_title = serializers.CharField(source="question.poll.title", read_only=True)
    poll_content_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserAnswer
        fields = [
            "id",
            "employee_id",
            "employee",
            "target_employee_id",
            "target_employee",
            "poll_content_object",
            "poll_id",
            "poll_title",
            "question",
            "question_title",
            "answer",
            "requires_attention",
            "created_at",
        ]

    def get_poll_content_object(self, obj: UserAnswer):
        content_type: ContentType = obj.question.poll.content_type
        object_id = obj.question.poll.object_id

        return (
            {
                "id": object_id,
                "type": content_type.model,
                "name": str(obj.question.poll.content_object),
            }
            if obj.question.poll.content_object
            else None
        )


class QuestionSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, source="useranswer_set", read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "question_type", "answers", "show"]


class PollQuestionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    related_object = serializers.SerializerMethodField()

    class Meta:
        model = PollQuestion
        fields = [
            "id",
            "title",
            "message",
            "time_of_day",
            "intended_for",
            "questions",
            "poll_type",
            "poll_number",
            "related_object",
        ]

    def get_related_object(self, obj: PollQuestion):
        """Метод для получения информации о связанном объекте."""
        if obj.content_object:
            return {
                "id": obj.object_id,
                "type": obj.content_type.model,
                "name": str(obj.content_object),
            }
        return None


class PlannedPollsListSerializer(serializers.ModelSerializer):
    # Тот самый сериализатор, который раньше был для ручки /polls через модель PollQuestion, а теперь через модель PollStatus
    poll_id = serializers.PrimaryKeyRelatedField(source="poll.id", read_only=True)
    title = serializers.CharField(source="poll.title", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    target_employee_name = serializers.SerializerMethodField(read_only=True)
    message = serializers.CharField(source="poll.message", read_only=True)
    days_after_hire = serializers.IntegerField(source="poll.days_after_hire")
    time_of_day = serializers.CharField(source="poll.time_of_day", read_only=True)
    intended_for = serializers.CharField(source="poll.intended_for", read_only=True)
    poll_type = serializers.CharField(source="poll.poll_type", read_only=True)
    poll_number = serializers.CharField(source="poll.poll_number", read_only=True)
    questions = QuestionSerializer(source="poll.questions", many=True, read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    related_object = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PollStatus
        fields = [
            "id",
            "employee_name",
            "target_employee_name",
            "poll_id",
            "title",
            "message",
            "days_after_hire",
            "time_of_day",
            "intended_for",
            "poll_type",
            "poll_number",
            "related_object",
            "created_by_admin",
            "is_archived",
            "started_at",
            "completed_at",
            "date_planned_at",
            "time_planned_at",
            "status",
            "status_display",
            "questions",
        ]

    def to_representation(self, instance):
        # Если были переданы сотрудник и таргет - пропускаем только ответы по этим условиям
        representation = super().to_representation(instance)

        filter_criteria = {
            "employee_id": self.context.get("employee"),
            "target_employee_id": self.context.get("target_employee"),
        }

        for question in representation.get("questions", []):
            question["answers"] = [
                answer
                for answer in question.get("answers", [])
                if all(
                    answer.get(key) == value
                    for key, value in filter_criteria.items()
                    if value is not None
                )
            ]

        return representation

    def get_target_employee_name(self, obj: PollStatus):
        return obj.target_employee.full_name if obj.target_employee else None

    def get_status_display(self, obj: PollStatus):
        return obj.get_status_display()

    def get_related_object(self, obj: PollStatus):
        """Метод для получения информации о связанном объекте."""

        if obj.poll.content_object:
            return {
                "id": obj.poll.object_id,
                "type": obj.poll.content_type.model,
                "name": str(obj.poll.content_object),
            }
        return None


class PollStatusWithPollSerializer(serializers.ModelSerializer):
    employee = serializers.StringRelatedField()
    target_employee = serializers.StringRelatedField()
    employee_id = serializers.PrimaryKeyRelatedField(source="employee", read_only=True)
    target_employee_id = serializers.PrimaryKeyRelatedField(
        source="target_employee", read_only=True
    )
    poll = PollQuestionSerializer(read_only=True)
    poll_status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PollStatus
        fields = [
            "id",
            "employee_id",
            "employee",
            "target_employee_id",
            "target_employee",
            "poll",
            "status",
            "poll_status_display",
            "started_at",
            "completed_at",
            "date_planned_at",
            "time_planned_at",
        ]

    def get_poll_status_display(self, obj: PollStatus):
        return obj.get_status_display()


class PollStatusSerializer(serializers.ModelSerializer):
    employee = serializers.StringRelatedField()
    target_employee = serializers.StringRelatedField()
    employee_id = serializers.PrimaryKeyRelatedField(source="employee", read_only=True)
    target_employee_id = serializers.PrimaryKeyRelatedField(
        source="target_employee", read_only=True
    )
    poll_title = serializers.SerializerMethodField(read_only=True)
    poll_status_display = serializers.SerializerMethodField(read_only=True)
    time_planned_at_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PollStatus
        fields = [
            "id",
            "employee_id",
            "employee",
            "target_employee_id",
            "target_employee",
            "poll_title",
            "status",
            "poll_status_display",
            "started_at",
            "completed_at",
            "date_planned_at",
            "time_planned_at",
            "time_planned_at_display",
        ]

    def get_poll_title(self, obj):
        """
        Метод для получения заголовка связанного опроса.
        """
        return obj.poll.title if obj.poll else None

    def get_poll_status_display(self, obj: PollStatus):
        return obj.get_status_display()

    def get_time_planned_at_display(self, obj: PollStatus):
        return obj.get_time_planned_at_display()


class PollStatusSkipSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=PollStatus.Status.choices)
    employee_full_name = serializers.CharField(
        source="employee.full_name", read_only=True
    )
    target_employee_full_name = serializers.CharField(
        source="target_employee.full_name", read_only=True
    )

    poll_title = serializers.SerializerMethodField(read_only=True)
    poll_status_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PollStatus
        fields = [
            "id",
            "status",
            "poll_status_display",
            "employee_full_name",
            "target_employee_full_name",
            "poll_title",
            "started_at",
            "completed_at",
            "date_planned_at",
            "time_planned_at",
        ]

    def update(self, instance: PollStatus, validated_data):
        instance.started_at = timezone.now()
        instance.status = PollStatus.Status.COMPLETED
        instance.completed_at = timezone.now()
        instance.save()
        instance.employee.update_onboarding_status()
        return instance

    def get_poll_title(self, obj):
        """
        Метод для получения заголовка связанного опроса.
        """
        return obj.poll.title if obj.poll else None

    def get_poll_status_display(self, obj: PollStatus):
        return obj.get_status_display()


class CreatePollSerializer(serializers.Serializer):
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), required=True
    )
    target_employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), required=False
    )
    poll = serializers.PrimaryKeyRelatedField(
        queryset=PollQuestion.objects.all(), required=True
    )
    date_planned_at = serializers.DateField(required=True)


class UserAnswerExportSerializer(serializers.Serializer):
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), many=True, required=False
    )
    target_employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), many=True, required=False
    )
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), many=True, required=False
    )
    poll = serializers.PrimaryKeyRelatedField(
        queryset=PollQuestion.objects.all(), many=True, required=False
    )
    poll_status = serializers.ChoiceField(
        choices=PollStatus.Status.choices, required=False
    )
    file_format = serializers.ChoiceField(choices=["xlsx"], required=False)
