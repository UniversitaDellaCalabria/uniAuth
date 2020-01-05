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
        self.login_data = dict(username='admin',
                               password='ingoalla')
        # create a dummy user
        self.user = self._get_superuser_user()
        
    def test_authn_def_sp(self):
        self.sp.is_active = 1
        self.sp.save()

        url, data = self._get_sp_authn_request()

        response = self.client.post(url, data, follow=True)
        assert 'id_username' in response.content.decode()

    def test_disabled_sp(self):
        self.sp.is_active = 0
        self.sp.save()

        url, data = self._get_sp_authn_request()

        response = self.client.post(url, data, follow=True)
        assert 'was disabled' in response.content.decode()

    def test_authn(self):
        self.sp.is_active = 1
        self.sp.save()

        url, data = self._get_sp_authn_request()

        response = self.client.post(url, data, follow=True)
        assert 'id_username' in response.content.decode()

    def test_account_attrs(self):
        # test accounts methods
        self.user.uid
        self.user.set_persistent_id(recipient_id=sp_eid,
                                    persistent_id='sd87f6sd78fsd87f6ds')
        logger.info('{}, uid: {}, persistent_id: {}'.format(self.user,
                                                            self.user.uid,
                                                            self.user.persistent_id(sp_eid)))
        # test persistent_id object repr
        logger.info(self.user.persistentid_set.get(recipient_id=sp_eid).__str__())

    def test_invalid_session(self):
        # authentication with invalid form, wrong password
        login_response = self.client.post(login_url, data=self.login_data, follow=True)
        assert 'Not a valid SAML Session' in login_response.content.decode()

    def test_invalid_form(self):
        url, data = self._get_sp_authn_request()
        response = self.client.post(url, data, follow=True)
        # authentication with invalid form, wrong password
        login_response = self.client.post(login_url, data=self.login_data, follow=True)
        assert 'is invalid' in login_response.content.decode()

    def test_valid_form(self):
        url, data = self._get_sp_authn_request()
        response = self.client.post(url, data, follow=True)
        # csrf_regexp = '<input type="hidden" name="csrfmiddlewaretoken" value="(?P<value>[a-zA-Z0-9+=]*)">'
        # login_data['csrfmiddlewaretoken'] = re.findall(csrf_regexp, response.content.decode())[0]
        self.login_data['password'] = 'admin'
        login_response = self.client.post(login_url,
                                          data=self.login_data, follow=True)
        # is there a SAML response?
        saml_resp = re.findall(samlresponse_form_regexp, login_response.content.decode())
        assert saml_resp

        # test agreement screens
        self.sp.agreement_screen = 1
        self.sp.save()
        login_response = self.client.post(login_url, data=self.login_data, follow=True)
        assert 'has requested the following informations' in login_response.content.decode()

        # don't show again
        agr_data = dict(dont_show_again=1, confirm=1)
        agr_url = reverse('uniauth:saml_user_agreement')
        agr_response = self.client.post(agr_url, data=agr_data, follow=True)

        # login again, agreement screen should not be displayed anymore
        # purge persistent_id from storage
        self.user.persistentid_set.all().delete()
        login_response = self.client.post(login_url, data=self.login_data, follow=True)
        saml_resp = re.findall(samlresponse_form_regexp, login_response.content.decode())
        assert saml_resp

        # transient name_id format, remove persistent_id
        sp_conf = copy.deepcopy(SAML_SP_CONFIG)
        del(sp_conf['service']['sp']['name_id_format'][0])
        self.sp_conf.load(sp_conf)
        url, data = self._get_sp_authn_request()
        response = self.client.post(url, data, follow=True)
        login_response = self.client.post(login_url, data=self.login_data, follow=True)
