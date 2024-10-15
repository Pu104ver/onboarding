from rest_framework import status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from api.serializers.analytics import (
    InAnalyticsEmployeesSerializer,
    InAnalyticsProjectsSerializer,
    EmployeeAnswersAnalyticsSerializer,
    CuratorAnswersAnalyticsSerializer,
    AnalyticsProjectsEmployeesSelfAnswersSerializer,
    AnalyticsProjectsCuratorsAnswersSerializer,
)
import analytics.services as analytics_services
from drf_yasg.utils import swagger_auto_schema


class AnalyticsEmployeeSelfAnswersViewSet(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=InAnalyticsEmployeesSerializer,
        responses={201: EmployeeAnswersAnalyticsSerializer(many=True)},
    )
    def post(self, request: Request):
        serializer = InAnalyticsEmployeesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        employees, employees_statistics, error = (
            analytics_services.calculate_employee_statistics(
                data=data, curator_answers=False
            )
        )

        if error:
            raise ValidationError(
                f"Ошибка при вычислении статистики сотрудников по их собственным ответам. {error}"
            )

        serializer = EmployeeAnswersAnalyticsSerializer(
            employees, employees_statistics=employees_statistics, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsEmployeeCuratorAnswersViewSet(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=InAnalyticsEmployeesSerializer,
        responses={201: CuratorAnswersAnalyticsSerializer(many=True)},
    )
    def post(self, request: Request):
        serializer = InAnalyticsEmployeesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        employees, employees_statistics, error = (
            analytics_services.calculate_employee_statistics(
                data=data,
                curator_answers=True,
            )
        )

        if error:
            raise ValidationError(
                f"Ошибка при вычислении статистики сотрудников по ответам кураторам. {error}"
            )

        serializer = CuratorAnswersAnalyticsSerializer(
            employees, employees_statistics=employees_statistics, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsProjectEmployeesSelfAnswersViewSet(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=InAnalyticsProjectsSerializer,
        responses={201: AnalyticsProjectsEmployeesSelfAnswersSerializer(many=True)},
    )
    def post(self, request: Request):
        serializer = InAnalyticsProjectsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        projects, projects_statistics, error = (
            analytics_services.calculate_project_statistics(
                data=data,
                curator_answers=False,
            )
        )

        if error:
            raise ValidationError(
                f"Ошибка при вычислении статистики проектов по ответам сотрудников. {error}"
            )

        serializer = AnalyticsProjectsEmployeesSelfAnswersSerializer(
            projects, projects_statistics=projects_statistics, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AnalyticsProjectCuratorsAnswersViewSet(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=InAnalyticsProjectsSerializer,
        responses={201: AnalyticsProjectsCuratorsAnswersSerializer(many=True)},
    )
    def post(self, request: Request):
        serializer = InAnalyticsProjectsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        projects, projects_statistics, error = (
            analytics_services.calculate_project_statistics(
                data=data,
                curator_answers=True,
            )
        )

        if error:
            raise ValidationError(
                f"Ошибка при вычислении статистики проектов по ответам кураторам. {error}"
            )

        serializer = AnalyticsProjectsCuratorsAnswersSerializer(
            projects, projects_statistics=projects_statistics, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
