from . base import *


class TestUnknowRP(BaseTestRP):

    def test_authn_request(self):
        url, data = self._get_sp_authn_request()

        # client = Client()
        response = self.client.post(url, data)

        assert response.status_code == 403 and \
               'Incorrectly signed' in response.content.decode()
        logging.info('IdP do not accept SP with unknow metadata -> OK')
