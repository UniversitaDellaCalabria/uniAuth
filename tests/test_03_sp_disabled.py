from django.conf import settings
from django.test import Client
from django.urls import reverse
from saml2.metadata import entity_descriptor

from .test_01_unknown_sp import *
from .test_02_sp import *

from .idp_pysaml2 import IDP_SP_METADATA_PATH


class TestRP(TestRP):
    def setUp(self):
        super().setUp()
        settings.SAML_DISALLOW_UNDEFINED_SP = True
        
    def test_authn_request(self):
        """
        a signed saml request from an UNDEFINED SP
        """
        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)

        client = Client()
        response = client.post(url, data)
        assert response.status_code == 403 and \
               'This SP is not allowed to access to this Service' in \
               response.content.decode()
