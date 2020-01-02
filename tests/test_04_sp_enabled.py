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

    def test_authn_def_sp(self):
        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)

        response = self.client.post(url, data, follow=True)
        assert 'id_username' in response.content.decode()

    def test_disabled_sp(self):
        sp = ServiceProvider.objects.first()
        sp.is_active = 0
        sp.save()

        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)

        response = self.client.post(url, data, follow=True)
        assert 'was disabled' in response.content.decode()
