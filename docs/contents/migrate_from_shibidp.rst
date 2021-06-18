Migrate from Shibboleth IdP
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here a brief description of the general steps to do for migrating an existing Shibboleth IdP to uniAuth, carrying the same configuration.
We have migrate from Shibboleth IdP 3.4.6 to uniAuth v2.0.0, here the steps we made to achieve this goal:

1. copy SAML2 certificates shibboleth idp SAML, from `credentials/` to your pysaml2 configuration.
2. Standing on Shibboleth metadata, in `metadata/idp-metadata.xml`, place the same Service Endpoints urls to your project's urls file::

    if 'uniauth_saml2_idp' in settings.INSTALLED_APPS:
        import uniauth_saml2_idp.urls
        from uniauth_saml2_idp.views import SsoEntryView, LogoutProcessView

        urlpatterns += path('idp/profile/SAML2/<str:binding>/SSO', SsoEntryView.as_view(),
                    name="saml_login_binding"),
        urlpatterns += path('idp/profile/SAML2/<str:binding>/SLO', LogoutProcessView.as_view(),
                    name="saml_logout_binding"),
        urlpatterns += path('idp/shibboleth/', metadata, name='saml2_idp_metadata'),

        urlpatterns += path(
            'idp/', include((uniauth_saml2_idp.urls, 'uniauth_saml2_idp',))
        ),

3. Configure the same entityID in your pysaml2 configuration.
4. Migrate the existing Shibboleth IdP `conf/attribute-filters.xml` (and any other available in `conf/services.xml`) to uniauth SP definitions (ModelAdmin or settings.py).
5. If you use LDAP: Configure PyMultiLDAP rewrite rules and pattern matching, standing on the Attributes defined in `conf/attribute-resolver.xml` (and any other available in `conf/services.xml).
6. Configure your metadata store (ModelAdmin or settings.py). It's suggested to use a MDQ Server for loading large federation xml files, as to be with eduGain.
7. Use uniauth `aacli` and `mdquery` commands to check the availability of Entities and the attribute to be released to them.
