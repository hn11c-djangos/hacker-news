"""
URL configuration for hacker_news project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny

from hacker_news.settings import openapi_info
from news import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi_info,
    public=True,
    permission_classes=[AllowAny],
    authentication_classes=[TokenAuthentication],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('news/', include('news.urls')),
    path('ask/', views.ask, name='ask'),
    path('newest/', views.newest, name='ask'),
    path('submit/', views.submit, name='submit'),  # Define el endpoint para /submit
    path('accounts/', include('allauth.urls')),  # Define el endpoint para /login
    path('user/', include('users.urls')),
    path('api/', include('apis.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', lambda request: redirect('news/', permanent=False)),
]
