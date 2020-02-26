# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.urls import path
from .views import UserProjectViewset, TasksViewSet, ProjectViewSet
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'users', UserProjectViewset)
router.register(r'tasks', TasksViewSet)
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]