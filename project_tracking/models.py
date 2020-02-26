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

    def get_total_task_seconds(self):
        start = self.started_at
        end = self.ended_at
        if not end:
            if self.is_paused:
                end = self.paused_at
            else:
                end = timezone.now()
        delta = end - start
        total_seconds = int(delta.total_seconds())
        return total_seconds

    @property
    def spend_time(self):
        total_seconds = self.get_total_task_seconds()
        hours, remainder = divmod(total_seconds, 60 * 60)
        minutes, seconds = divmod(remainder, 60)
        return '{} hrs {} mins {} secs'.format(hours, minutes, seconds)

    @property
    def is_paused(self):
        """
        Determine whether or not this entry is paused
        """
        return bool(self.paused_at)

    @property
    def is_closed(self):
        """
        Determine whether this entry has been closed or not
        """
        return bool(self.ended_at)

    def pause(self):
        """
        If this entry is not paused, pause it.
        """
        if not self.is_paused:
            self.paused_at = timezone.now()
            self.save()

    def unpause(self):
        if self.is_paused:
            delta = timezone.now() - self.paused_at
            self.seconds_paused += delta.seconds
            self.paused_at = None
            self.save()

    def toggle_paused(self):
        """
        Toggle the paused state of this entry.  If the entry is already paused,
        it will be unpaused; if it is not paused, it will be paused.
        """
        if self.is_paused:
            self.unpause()
        else:
            self.pause()

    def close(self):
        if self.is_paused:
            self.unpause()
        self.ended_at = timezone.now()
        self.save()

    def restart(self):
        self.started_at = timezone.now()
        self.ended_at = None
        self.seconds_paused = 0
        self.paused_at = None
        self.save()