import json
import re

from django.conf import settings
from django.urls import reverse

from uniauth.models import ServiceProvider
from .base import *
from .idp_pysaml2 import IDP_SP_METADATA_PATH
from .settingsldap import LDAP_CONNECTIONS


class TestEnabledRP(BaseTestRP):
    def setUp(self):
        super().setUp()
        self._add_sp_md()
        settings.SAML_DISALLOW_UNDEFINED_SP = True
        self._add_sp()
        self.sp = ServiceProvider.objects.first()
        self.login_data = dict(username='mario',
                               password='cimpa12')
        # add LDAP in settings
        settings.INSTALLED_APPS.append('multildap')
        settings.LDAP_CONNECTIONS = LDAP_CONNECTIONS
        settings.AUTHENTICATION_BACKENDS.append('idp.multildap_auth.LdapUnicalMultiAcademiaAuthBackend')
        
        # disable agreement screen
        self.sp.agreement_screen = 0

        # configure sp processors
        self.sp.attribute_processor = 'idp.processors.LdapUnicalMultiAcademiaProcessor'
        self.sp.attribute_mapping = json.dumps({
            # refeds + edugain Entities
            "cn": "cn",
            "eduPersonEntitlement": "eduPersonEntitlement",
            "eduPersonPrincipalName": "eduPersonPrincipalName",
            "schacHomeOrganization": "schacHomeOrganization",
            "eduPersonHomeOrganization": "eduPersonHomeOrganization",
            "eduPersonAffiliation": "eduPersonAffiliation",
            "eduPersonScopedAffiliation": "eduPersonScopedAffiliation",
            "eduPersonTargetedID": "eduPersonTargetedID",
            "mail": ["mail", "email"],
            "email": ["mail", "email"],
            "schacPersonalUniqueCode": "schacPersonalUniqueCode",
            "schacPersonalUniqueID": "schacPersonalUniqueID",
            "sn": "sn",
            "givenName": ["givenName", "another_possible_occourrence"],
            "displayName": "displayName",
    
            # custom attributes
            "codice_fiscale": "codice_fiscale",
            "matricola_studente": "matricola_studente",
            "matricola_dipendente": "matricola_dipendente"
        })
        self.sp.save()
        
    def test_valid_form(self):
        url, data = self._get_sp_authn_request()
        response = self.client.post(url, data, follow=True)
        login_response = self.client.post(login_url,
                                          data=self.login_data, follow=True)
        # is there a SAML response?
        saml_resp = re.findall(samlresponse_form_regexp,
                               login_response.content.decode())
        assert saml_resp
