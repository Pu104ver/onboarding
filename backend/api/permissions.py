from rest_framework.permissions import BasePermission, SAFE_METHODS
from employees.models import Employee


class IsAdminOrHR(BasePermission):
    """
    Разрешение на создание и редактирование сотрудников только для администраторов и HR.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            employee = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            return False

        return employee.role in [Employee.RoleChoices.ADMIN, Employee.RoleChoices.HR]


class IsReadOnly(BasePermission):
    """
    Разрешение только на чтение
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
