import re

from django.conf import settings
from django.urls import reverse

from uniauth.models import ServiceProvider
from .base import *
from .idp_pysaml2 import IDP_SP_METADATA_PATH


class TestEnabledRP(BaseTestRP):
    def setUp(self):
        super().setUp()
        self._add_sp_md()
        settings.SAML_DISALLOW_UNDEFINED_SP = True
        self._add_sp()
        self.sp = ServiceProvider.objects.first()

    def test_authn_def_sp(self):
        self.sp.is_active = 1
        self.sp.save()
        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)

        response = self.client.post(url, data, follow=True)
        assert 'id_username' in response.content.decode()

    def test_disabled_sp(self):
        self.sp.is_active = 0
        self.sp.save()

        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)

        response = self.client.post(url, data, follow=True)
        assert 'was disabled' in response.content.decode()

    def test_authn(self):
        self.sp.is_active = 1
        self.sp.save()

        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)

        response = self.client.post(url, data, follow=True)
        assert 'id_username' in response.content.decode()

        # create a dummy user
        user = self._get_superuser_user()
        # test accounts methods
        # user.__str__()
        user.uid
        user.set_persistent_id(recipient_id=sp_eid,
                               persistent_id='sd87f6sd78fsd87f6ds')
        logger.info('{}, uid: {}, persistent_id: {}'.format(user,
                                                            user.uid,
                                                            user.persistent_id(sp_eid)))
        # test persistent_id object repr
        logger.info(user.persistentid_set.get(recipient_id=sp_eid).__str__())


        # authentication with invalid form, wrong password
        login_data = dict(username=user.username,
                          password='ingoalla')
        login_process = reverse('uniauth:saml_login_process')
        login_url = reverse('uniauth:login')+'?next={}'.format(login_process)
        login_response = self.client.post(login_url, data=login_data, follow=True)
        assert 'is invalid' in login_response.content.decode()

        # valid form
        # csrf_regexp = '<input type="hidden" name="csrfmiddlewaretoken" value="(?P<value>[a-zA-Z0-9+=]*)">'
        # login_data['csrfmiddlewaretoken'] = re.findall(csrf_regexp, response.content.decode())[0]
        login_data['password'] = user.username

        login_response = self.client.post(login_url,
                                          data=login_data, follow=True)

        # is there a SAML response?
        resp_regexp = 'name="SAMLResponse" value="(?P<value>[a-zA-Z0-9+=]*)"'
        saml_resp = re.findall(resp_regexp, login_response.content.decode())
        assert saml_resp

        # test agreement screens
        self.sp.agreement_screen = 1
        self.sp.save()
        login_response = self.client.post(login_url, data=login_data, follow=True)

        assert 'has requested the following informations' in login_response.content.decode()
