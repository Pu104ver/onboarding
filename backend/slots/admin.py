from django.contrib import admin

from slots.models import Slot


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "date", "booked_by")
    list_filter = ("booked_by", "date")
    readonly_fields = ("id",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "start_time",
                    "date",
                    "booked_by",
                ),
            },
        ),
    )
