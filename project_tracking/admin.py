from django.contrib import admin
from .models import Project, Task


class TaskInlineAdmin(admin.StackedInline):
    model = Task
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'cloned_from')
    raw_id_fields = ('cloned_from', )


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',  'user')
    raw_id_fields = ('user',)
    inlines = [TaskInlineAdmin, ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
