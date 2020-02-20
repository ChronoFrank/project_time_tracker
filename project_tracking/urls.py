# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from .views import UserProjectViewset
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'users', UserProjectViewset)

urlpatterns = [
    url(r'^', include(router.urls)),
]