# -*- coding: utf-8 -*-
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserProjectSerializer, TaskSerializer
from django.contrib.auth.models import User
from .models import Task, Project
from datetime import datetime, timedelta
from django.utils import timezone


class UserProjectViewset(ModelViewSet):
    """
    Small ViewSet  to handle no admin users
    retrieve:
        Return a serialized user instance.
    list:
        Return all users, ordered by most recently joined.
    create:
        Create a new user.
    """
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserProjectSerializer
    http_method_names = ['get', 'post']
    permission_classes = [IsAdminUser, IsAuthenticated]


class TasksViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['get', 'post', 'put']
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def list(self, request, *args, **kwargs):
        query_set = self.get_queryset().filter(user=request.user).order_by('-started_at')
        page = self.paginate_queryset(query_set)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(query_set, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        running_tasks = Task.objects.filter(user=request.user, ended_at__isnull=True, paused_at__isnull=True)
        if running_tasks.exists():
            return Response({'error': 'there are tasks running, '
                                      'you must pause or terminate'
                                      ' them in order to create new tasks'}, status=status.HTTP_403_FORBIDDEN)
        else:
            project_id = request.data.get('project_id')
            task_name = request.data.get('name')
            duration = request.data.get('duration')
            if not project_id:
                return Response({'error': 'You must provide a project'
                                          ' in order to start a new task'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                started_at = timezone.now()
                params = {
                    "user": request.user,
                    "name": task_name,
                    "started_at": started_at
                }
                try:
                    project = Project.objects.get(id=int(project_id))
                    params.update({"project": project})
                except (Project.DoesNotExist, ValueError) as e:
                    return Response({'error': 'Invalid Project'}, status=status.HTTP_400_BAD_REQUEST)

                if duration:
                    try:
                        time_obj = datetime.strptime('01:15:05', '%H:%M:%S')
                        ended_at = started_at + timedelta(hours=time_obj.hour,
                                                          minutes=time_obj.minute,
                                                          seconds=time_obj.second)
                        params.update({"ended_at": ended_at})
                    except ValueError:
                        return Response({'error': 'Invalid duration, format must be H:M:S'},
                                        status=status.HTTP_400_BAD_REQUEST)

                new_task = Task.objects.create(**params)

            return Response(TaskSerializer(instance=new_task).data, status=status.HTTP_200_OK)

    @action(methods=['put', ], detail=False, url_path='pause_resume/(?P<pk>\d+)')
    def pause_resume_task(self, request, pk):
        try:
            task = Task.objects.get(id=int(pk))
        except Task.DoesNotExist:
            return Response({'detail': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        task.pause()
        return Response(TaskSerializer(instance=task).data, status=status.HTTP_200_OK)

