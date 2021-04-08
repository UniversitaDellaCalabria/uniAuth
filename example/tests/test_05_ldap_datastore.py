import base64
import json
import re

from django.conf import settings
from django.urls import reverse

from saml2.config import SPConfig
from saml2.metadata import entity_descriptor
from uniauth_saml2_idp.models import ServiceProvider

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
        settings.AUTHENTICATION_BACKENDS.append('uniauth_saml2_idp.auth.multildap.LdapUnicalMultiAcademiaAuthBackend')

        # disable agreement screen
        self.sp.agreement_screen = 0

        # configure sp processors
        self.sp.attribute_processor = 'uniauth_saml2_idp.processors.ldap.LdapUnicalMultiAcademiaProcessor'
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

        # run ldapd
        self._run_ldapd()

    def test_valid_form(self):
        url, data, session_id = self._get_sp_authn_request()
        response = self.client.post(url, data, follow=True)
        login_response = self.client.post(login_url,
                                          data=self.login_data, follow=True)
        # is there a SAML response?
        saml_resp = re.findall(samlresponse_form_regexp,
                               login_response.content.decode())
        assert saml_resp

        # login again to update existing user on db
        login_response = self.client.post(login_url,
                                          data=self.login_data, follow=True)

        # test a disabled user
        #user = get_user_model().objects.last()
        #user.is_active = 0
        #user.save()
        #login_response = self.client.post(login_url,
                                          #data=self.login_data, follow=True)

    def test_invalid_form(self):
        url, data, session_id = self._get_sp_authn_request()
        response = self.client.post(url, data, follow=True)
        login_data = {'username':'mario', 'password':'erewr'}
        login_response = self.client.post(login_url,
                                          data=login_data,
                                          follow=True)
        assert 'is invalid' in login_response.content.decode()

        login_data = {'username':'dsfhdsjkfh', 'password':'erewr'}
        login_response = self.client.post(login_url,
                                          data=login_data,
                                          follow=True)
        assert 'is invalid' in login_response.content.decode()


    def test_sp_attr_policy(self):
        # create a pysaml SP
        self.sp_conf = SPConfig()
        _sp_conf = copy.deepcopy(SAML_SP_CONFIG)
        _sp_conf['service']['sp']['required_attributes'] = ['email',
                                                            'givenName',
                                                            'eduPersonPrincipalName',
                                                            'sn',
                                                            'displayName']
        self.sp_conf.load(_sp_conf)
        # put sp metadata into IDP md store
        sp_metadata = entity_descriptor(self.sp_conf)
        with open(IDP_SP_METADATA_PATH+'/sp.xml', 'wb') as fd:
            fd.write(sp_metadata.to_string())

        sp_client = Saml2Client(self.sp_conf)
        session_id, result = sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)
        response = self.client.post(url, data, follow=True)
        # login again to update existing user on db
        login_response = self.client.post(login_url,
                                          data=self.login_data, follow=True)
        # is there a SAML response?
        saml_resp = re.findall(samlresponse_form_regexp,
                               login_response.content.decode())
        assert saml_resp
        saml_assrt = base64.b64decode(saml_resp[0]).decode()
        assert 'sn' in saml_assrt

    def test_sp_attr_policy2(self):
        # create a pysaml SP
        self.sp_conf = SPConfig()
        _sp_conf = copy.deepcopy(SAML_SP_CONFIG)
        _sp_conf['service']['sp']['required_attributes'] = ['email',
                                                            'givenName',
                                                            'eduPersonPrincipalName',
                                                            'sn',
                                                            'telexNumber']
        self.sp_conf.load(_sp_conf)
        # put sp metadata into IDP md store
        sp_metadata = entity_descriptor(self.sp_conf)
        with open(IDP_SP_METADATA_PATH+'/sp.xml', 'wb') as fd:
            fd.write(sp_metadata.to_string())

        sp_client = Saml2Client(self.sp_conf)
        session_id, result = sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)
        response = self.client.post(url, data, follow=True)
        # login again to update existing user on db
        login_response = self.client.post(login_url,
                                          data=self.login_data, follow=True)
        # is there a SAML response?
        saml_resp = re.findall(samlresponse_form_regexp,
                               login_response.content.decode())
        # assert saml_resp
        # saml_assrt = base64.b64decode(saml_resp[0]).decode()
        # assert 'telexNumber' not in saml_assrt

    def tearDown(self):
        """Kill ldapd test server
        """
        self.ldapd.kill()
