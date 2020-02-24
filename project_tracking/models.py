from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Project(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    cloned_from = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(default='Unnamed task', max_length=250)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)
    seconds_paused = models.PositiveIntegerField(default=0)
    paused_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{0}-{1}'.format(self.name, self.project)

    @property
    def spend_time(self):
        start = self.started_at
        end = self.ended_at
        if not end:
            end = timezone.now()
        delta = end - start
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        return '{} hrs {} mins {} secs'.format(hours, minutes, seconds)

