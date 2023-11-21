"""django_idp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
# from uniauth_saml2_idp.views import LoginAuthView

import os

admin.site.site_title = os.getenv("ADMIN_UI_HEADER", 'uniAuth-IAM')
admin.site.index_title = os.getenv("ADMIN_UI_HEADER", 'uniAuth Administration Backend')
admin.site.site_header = os.getenv("ADMIN_UI_HEADER",'uniAuth Administration Backend')


urlpatterns = [
    path('{}/'.format(getattr(settings, 'ADMIN_PATH', 'admin')),
         admin.site.urls),
    path('logout/', LogoutView.as_view(),
         {'next_page': settings.LOGOUT_REDIRECT_URL},
         name='logout'),
    # path('login/', LoginAuthView.as_view(), name='login'),
]

if 'uniauth_saml2_idp' in settings.INSTALLED_APPS:
    import uniauth_saml2_idp.urls
    urlpatterns += path(
        'idp/', include((uniauth_saml2_idp.urls, 'uniauth_saml2_idp',))
    ),

if 'allauth' in settings.INSTALLED_APPS:
    urlpatterns += path('accounts/', include('allauth.urls')),
    
if 'password_reset' in settings.INSTALLED_APPS:
    import password_reset.urls
    urlpatterns += (path("", include(password_reset.urls)),)

if 'mfa' in settings.INSTALLED_APPS:
    urlpatterns += (path('mfa/', include('mfa.urls', namespace='mfa')),)
