from django.contrib import admin
from .models import Banana


@admin.register(Banana)
class BananaAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "days_old", "created_at", "updated_at"]
    list_filter = ["status", "created_at"]
    readonly_fields = ["created_at", "updated_at", "days_old"]

    def days_old(self, obj):
        return obj.days_old

    days_old.short_description = "Days Old"
