from django.test import Client
from django.urls import reverse
from saml2.metadata import entity_descriptor

from .test_01_unknown_sp import *
from .idp_pysaml2 import IDP_SP_METADATA_PATH


class TestRP(TestUnknowRP):
    def setUp(self):
        super().setUp()

        # put sp metadata into IDP md store
        sp_metadata = entity_descriptor(self.sp_conf)
        with open(IDP_SP_METADATA_PATH+'/sp.xml', 'wb') as fd:
            fd.write(sp_metadata.to_string())

    def test_unsigned_authn_request(self):
        """
        a UNsigned saml request from a well know SP
        """
        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST,
                                             sign=False,
                                             sigalg=None)
        url, data = extract_saml_authn_data(result)

        client = Client()
        response = client.post(url, data)
        # forbidden !
        assert response.status_code == 403 and \
               'Incorrectly signed' in response.content.decode()

        
    def test_authn_request(self):
        """
        a signed saml request from a well know SP
        """
        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)

        client = Client()
        response = client.post(url, data)

        login_url = reverse('uniauth:saml_login_process')
        assert response.status_code == 302 and \
               response._headers['location'][1] == login_url

    
