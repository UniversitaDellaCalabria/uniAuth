from django.urls import include, path
from django.contrib import admin
from django.contrib.auth.views import LoginView

import uniauth

urlpatterns = [
    path('idp/', include('uniauth.urls')),
]
