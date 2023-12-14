from django.conf import settings
from django.urls import path, include

from . import views

app_name = "uniauth_saml2_idp"

urlpatterns = [
    path("sso/<str:binding>", views.SSOEntryView.as_view(),
         name="saml_login_binding"),
    path("login/process/", views.LoginProcessView.as_view(),
         name="saml_login_process"),
    path(
        "login/process_user_agreement/",
        views.UserAgreementScreen.as_view(),
        name="saml_user_agreement",
    ),
    path(
        "slo/<str:binding>",
        views.LogoutProcessView.as_view(),
        name="saml_logout_binding",
    ),
    path("metadata/", views.metadata, name="saml2_idp_metadata"),
    path("test/500/", views.test500, name="test500"),
]

if 'mfa' in settings.INSTALLED_APPS:
    urlpatterns.append(
        path('login/', views.LoginMfaView.as_view(), name="login")
    )
else:
    urlpatterns.append(
        path("login/", views.LoginAuthView.as_view(), name="login")
    )
