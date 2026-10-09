from django.contrib import admin, messages
from django.db.models import QuerySet

from indexing import models, run_job, stop_job


class CreateIndexAdmin(admin.StackedInline):
    model = models.CreateIndexTask
    extra = 0


class ReindexAdmin(admin.StackedInline):
    model = models.ReindexTask
    extra = 0


class PopulateIndexAdmin(admin.StackedInline):
    model = models.PopulateIndexTask
    extra = 0


class UpdateIndexAdmin(admin.StackedInline):
    model = models.UpdateIndexTask
    extra = 0


class UpdateSettingsAdmin(admin.StackedInline):
    model = models.UpdateSettingsTask
    extra = 0


class RemoveAliasAdmin(admin.StackedInline):
    model = models.RemoveAliasTask
    extra = 0


class AddAliasAdmin(admin.StackedInline):
    model = models.AddAliasTask
    extra = 0


class DeleteIndexAdmin(admin.StackedInline):
    model = models.DeleteIndexTask
    extra = 0



class IndexJobAdmin(admin.ModelAdmin):
    list_display = ['created', 'corpus', 'status']
    readonly_fields = ['status']
    list_filter = ['corpus']
    inlines = [
        CreateIndexAdmin,
        ReindexAdmin,
        PopulateIndexAdmin,
        UpdateIndexAdmin,
        UpdateSettingsAdmin,
        RemoveAliasAdmin,
        AddAliasAdmin,
        DeleteIndexAdmin,
    ]
    actions = ['start_job']

    @admin.action(description='Start selected jobs')
    def start_job(self, request, queryset: QuerySet[models.IndexJob]):
        for job in queryset:
            run_job.perform_indexing_async(job)
            self.message_user(
                request,
                f'Index job {job} started!',
                messages.SUCCESS,
            )

    @admin.action(description='Stop selected jobs')
    def stop_job(self, request, queryset: QuerySet[models.IndexJob]):
        for job in queryset:
            if stop_job.is_stoppable(job):
                stop_job.mark_tasks_stopped(job)
                self.message_user(
                    request,
                    f'Index job {job} stopped!',
                    messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    f'Index job {job} cannot be stopped because it is not running',
                    messages.WARNING,
                )


admin.site.register(models.IndexJob, IndexJobAdmin)
