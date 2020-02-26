from django.contrib import admin
from .models import Project, Task


class TaskInlineAdmin(admin.StackedInline):
    model = Task
    extra = 0


class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'project', 'cloned_from')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', )
    inlines = [TaskInlineAdmin, ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)
