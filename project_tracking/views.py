# -*- coding: utf-8 -*-
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from .serializers import UserProjectSerializer
from django.contrib.auth.models import User


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
    http_method_names = ['get', 'post' ]
    permission_classes = [IsAdminUser, IsAuthenticated]