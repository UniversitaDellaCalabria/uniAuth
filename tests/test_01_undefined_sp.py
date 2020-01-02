from . base import *


class TestUnknowRP(BaseTestRP):

    def test_authn_request(self):
        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST,
                                             )
                                             #sign=False,
                                             #sigalg=None)

        url, data = extract_saml_authn_data(result)

        # client = Client()
        response = self.client.post(url, data)

        assert response.status_code == 403 and \
               'Incorrectly signed' in response.content.decode()
        logging.info('IdP do not accept SP with unknow metadata -> OK')
