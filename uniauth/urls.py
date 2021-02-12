from django.urls import path

from . import views

app_name = 'uniauth'

urlpatterns = [
    path('login/', views.LoginAuthView.as_view(), name='login'),
    # path('sso/init', views.SSOInitView.as_view(), name="saml_idp_init"),
    path('sso/<str:binding>', views.sso_entry, name="saml_login_binding"),
    path('login/process/', views.LoginProcessView.as_view(),
         name='saml_login_process'),
    #  path('login/process_multi_factor/', views.get_metadata,
         #  name='saml_multi_factor'),
    path('login/process_user_agreement/',
         views.UserAgreementScreen.as_view(), name='saml_user_agreement'),
    path('slo/<str:binding>', views.LogoutProcessView.as_view(),
         name="saml_logout_binding"),
    path('metadata/', views.idp_metadata, name='saml2_idp_metadata'),

    path('test/500/', views.test500, name='test500'),
    
    path('aa/metadata/', views.aa_metadata, name='saml2_aa_metadata'),
    path('aap/', views.attribute_query_service, name='aap'),
]
