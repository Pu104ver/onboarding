from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, AuthenticationApplication, AuthenticationToken


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "first_name", "last_name", "is_staff")
    ordering = ("-id",)
    search_fields = ("email", "first_name", "last_name")
    readonly_fields = ("id", "last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


@admin.register(AuthenticationApplication)
class AuthenticationApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_id', 'client_secret', 'name')


@admin.register(AuthenticationToken)
class AuthenticationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'expires_in', 'application')
