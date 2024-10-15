from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authentication import TokenAuthentication
from api.auth.token import CustomAuthToken
from api.views.employees import (
    EmployeeViewSet,
    CuratorEmployeeViewSet,
    CuratorEmployeeBulkCreateAPIView,
    MeAPIView,
    EmployeeStatusListView,
    EmployeeRiskStatusListView,
)
from api.views.projects import (
    ProjectViewSet,
    ProjectAssignmentViewSet,
    ProjectAssignmentBulkCreateAPIView,
)
from api.views.comments import CommentViewSet
from api.views.slots import SlotViewSet
from api.views.users import CustomUserViewSet
from api.views.questions import (
    PlannedPollsListView,
    PollStatusTypesListView,
    UserAnswerListView,
    CompletePollStatusView,
    EmployeePollsWithAnswersView,
    ExportAnswersView,
    AvailablePollQuestionsView,
    CreatePollView,
)
from api.views.feedback import FeedbackUserViewSet
from api.views.analytics import (
    AnalyticsEmployeeSelfAnswersViewSet,
    AnalyticsEmployeeCuratorAnswersViewSet,
    AnalyticsProjectEmployeesSelfAnswersViewSet,
    AnalyticsProjectCuratorsAnswersViewSet,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="API",
        default_version="v1",
        description="API documentation for Snippets",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(
            email="contact@snippets.local", url="https://t.me/dumplings_enjoyer"
        ),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    authentication_classes=(TokenAuthentication,),
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(
    r"curator-employees", CuratorEmployeeViewSet, basename="curator-employees"
)
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"projects", ProjectViewSet, basename="project")
router.register(
    r"project-assignments", ProjectAssignmentViewSet, basename="project-assignments"
)
router.register(r"users", CustomUserViewSet, basename="user")
router.register(r"feedback", FeedbackUserViewSet, basename="feedback")
router.register(f"slots", SlotViewSet, basename="slots")

urlpatterns = [
    path("", include(router.urls)),
    path("api-token-auth/", CustomAuthToken.as_view(), name="api_token_auth"),
    path(
        "analytics-employee-self-answers/",
        AnalyticsEmployeeSelfAnswersViewSet.as_view(),
        name="analytics-employee-self-answers",
    ),
    path(
        "analytics-employee-curators-answers/",
        AnalyticsEmployeeCuratorAnswersViewSet.as_view(),
        name="analytics-employee-curators-answers",
    ),
    path(
        "analytics-projects-employees-self-answers/",
        AnalyticsProjectEmployeesSelfAnswersViewSet.as_view(),
        name="analytics-projects-employees-self-answers",
    ),
    path(
        "analytics-projects-curators-answers/",
        AnalyticsProjectCuratorsAnswersViewSet.as_view(),
        name="analytics-projects-curators-answers",
    ),
    path("me/", MeAPIView.as_view(), name="me"),
    path(
        "available-polls/",
        AvailablePollQuestionsView.as_view(),
        name="available-polls",
    ),
    path("create-poll/", CreatePollView.as_view(), name="create-poll"),
    path("polls/", PlannedPollsListView.as_view(), name="polls-list"),
    path(
        "poll-statuses-types/",
        PollStatusTypesListView.as_view(),
        name="poll-status-list",
    ),
    path(
        "employee-statuses/",
        EmployeeStatusListView.as_view(),
        name="employee-status-list",
    ),
    path(
        "employee-risk-statuses/",
        EmployeeRiskStatusListView.as_view(),
        name="employee-risk-status-list",
    ),
    path("user-answers/", UserAnswerListView.as_view(), name="user-answers"),
    path(
        "curator-employees-bulk-create/",
        CuratorEmployeeBulkCreateAPIView.as_view(),
        name="curator-employee-bulk-create",
    ),
    path(
        "project-assignments-bulk-create/",
        ProjectAssignmentBulkCreateAPIView.as_view(),
        name="project-assignment-bulk-create",
    ),
    path(
        "complete-poll-status/<int:poll_status_id>/",
        CompletePollStatusView.as_view(),
        name="complete-poll-status",
    ),
    path(
        "employee-polls-with-answers/<int:employee_id>/",
        EmployeePollsWithAnswersView.as_view(),
        name="employee-polls-with-answers",
    ),
    path("export-answers/", ExportAnswersView.as_view(), name="export_answers"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
