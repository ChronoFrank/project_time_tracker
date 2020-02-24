# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.urls import path
from .views import UserProjectViewset, TasksView
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'users', UserProjectViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
    path(r'tasks/', TasksView.as_view(), name='list_tasks'),
]