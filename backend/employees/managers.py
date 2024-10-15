from django.db import models
from django.db.models import (
    Case,
    When,
    Value,
    IntegerField,
    QuerySet,
)
from questions.models import PollStatus
from typing import Optional
from core.managers import SoftDeleteManager


class EmployeeManager(SoftDeleteManager):
    def curators_for_projects(self, projects_ids: QuerySet) -> QuerySet:
        """
        Находит кураторов для переданных проектов.

        Args:
            projects_ids (QuerySet): queryset идентификаторов проектов
        Returns:
            QuerySet: queryset кураторов для переданных проектов
        """
        return self.filter(
            role="curator",
            projects_assigned__project_id__in=models.Subquery(projects_ids),
        ).distinct()

    def sort_by_poll_completion(self, queryset: Optional[QuerySet] = None):
        """
        Сортирует сотрудников по времени завершения опроса от позднего к раннему.
        В случае одинакового времени завершения опроса, сортируются по статусу опроса сотрудника.
        Если параметр queryset не передан, то используется self.get_queryset.

        Args:
            queryset (QuerySet): queryset сотрудников
        Returns:
            QuerySet: queryset сотрудников отсортированных по времени завершению опроса от позднего к раннему
        """
        queryset: QuerySet = queryset or self.get_queryset()

        queryset = queryset.annotate(
            status_order=Case(
                When(
                    onboarding_status__status=PollStatus.Status.EXPIRED, then=Value(0)
                ),
                When(
                    onboarding_status__status=PollStatus.Status.IN_FROZEN, then=Value(1)
                ),
                When(
                    onboarding_status__status=PollStatus.Status.IN_PROGRESS,
                    then=Value(2),
                ),
                When(
                    onboarding_status__status=PollStatus.Status.NOT_STARTED,
                    then=Value(3),
                ),
                When(
                    onboarding_status__status=PollStatus.Status.COMPLETED, then=Value(4)
                ),
                default=Value(5),
                output_field=IntegerField(),
            )
        )
        queryset = queryset.order_by(
            Case(
                When(onboarding_status__completed_at__isnull=True, then=Value(1)),
                When(onboarding_status__completed_at__isnull=False, then=Value(0)),
                output_field=IntegerField(),
            ),
            "-onboarding_status__completed_at",
            "status_order",
            "-id",
        )

        return queryset
