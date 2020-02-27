# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import Project, Task


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'name', 'started_at', 'ended_at', 'spend_time', 'is_paused', 'seconds_paused', 'is_closed')


class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True,  max_length=200,
                                 validators=[UniqueValidator(queryset=Project.objects.all())])

    class Meta:
        model = Project
        fields = ('id', 'name', 'total_spend_time', 'project_tasks')


class UserProjectSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=32)
    project_set = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'project_set')

