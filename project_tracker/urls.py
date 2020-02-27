# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from django.contrib import admin
from project_tracking import urls as project_tracking_urls
from rest_framework.documentation import include_docs_urls


api_v1 = [
    url(r'^api/v1/access_token/$', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/v1/refresh_token/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    url(r'^api/v1/', include(project_tracking_urls))
]

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title='Project Tracker API Documentation')),
] + api_v1

