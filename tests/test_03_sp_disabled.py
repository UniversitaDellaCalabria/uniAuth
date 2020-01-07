from django.conf import settings
from django.urls import reverse

from .base import *
from .idp_pysaml2 import IDP_SP_METADATA_PATH


class TestUndefinedRP(BaseTestRP):
    def setUp(self):
        super().setUp()
        self._add_sp_md()
        settings.SAML_DISALLOW_UNDEFINED_SP = True

    def test_authn_request(self):
        """
        a signed saml request from an UNDEFINED SP
        """
        url, data = self._get_sp_authn_request()

        response = self.client.post(url, data, follow=True)
        assert response.status_code == 403 and \
               'This SP is not allowed to access to this Service' in \
               response.content.decode()
