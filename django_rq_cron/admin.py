from django.contrib import admin
from django.utils import timezone

from django_rq_cron.models import CronJob, CronJobRun, CronJobStatusTransition


class CronJobRunInline(admin.TabularInline):
    model = CronJobRun
    fields = ("status", "creation_date", "completion_date", "error")
    readonly_fields = ("status", "creation_date", "completion_date", "error")
    extra = 0
    max_num = 0


class CronJobStatusTransitionInline(admin.TabularInline):
    model = CronJobStatusTransition
    fields = ("creation_date", "old_value", "new_value")
    readonly_fields = ("creation_date", "old_value", "new_value")
    extra = 0
    max_num = 0


@admin.register(CronJob)
class CronJobAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "cadence",
        "status",
        "latest_run_date",
        "latest_status_change",
        "human_readable_time_since_status_change",
    )
    list_filter = ("status", "cadence")
    search_fields = ("name", "description")
    readonly_fields = (
        "latest_run_date",
        "latest_status_change",
        "human_readable_time_since_status_change",
    )
    inlines = (CronJobRunInline, CronJobStatusTransitionInline)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "cadence",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "latest_run_date",
                    "latest_status_change",
                    "human_readable_time_since_status_change",
                )
            },
        ),
    )


@admin.register(CronJobRun)
class CronJobRunAdmin(admin.ModelAdmin):
    list_display = (
        "cron_job",
        "status",
        "creation_date",
        "completion_date",
        "processing_time",
    )
    list_filter = ("status", "cron_job")
    search_fields = ("cron_job__name", "error")
    readonly_fields = (
        "cron_job",
        "status",
        "creation_date",
        "completion_date",
        "error",
        "data",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "cron_job",
                    "status",
                    "creation_date",
                    "completion_date",
                    "error",
                    "data",
                )
            },
        ),
    )

    def processing_time(self, obj):
        if obj.completion_date:
            return (obj.completion_date - obj.creation_date).total_seconds()
        if obj.status == CronJobRun.Status.IN_PROGRESS:
            return (timezone.now() - obj.creation_date).total_seconds()
        return None

    processing_time.short_description = "Processing Time (s)"
