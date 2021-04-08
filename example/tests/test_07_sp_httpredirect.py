import saml2

from django.conf import settings
from django.urls import reverse
from saml2 import BINDING_HTTP_REDIRECT

from . base import *


class TestRP(BaseTestRP):
    def setUp(self):
        super().setUp()
        self._superuser_login()
        self._add_sp_md()

    def test_authn_request_redirect(self):
        """
        HTTP-REDIRECT login
        """

        # pySAML2 TODO
        # HTTP-REDIRECT Signed AuthnRequest are faulty
        return None
        # end pySAML2 TODO

        session_id, result = self.sp_client.prepare_for_authenticate(
                                     entityid=idp_eid,
                                     relay_state='/',
                                     binding=BINDING_HTTP_REDIRECT)
        url, data = extract_saml_authn_data(result)

        response = self.client.get(url, follow=True)
        assert response.status_code == 200

        login_process_url = reverse('uniauth_saml2_idp:saml_login_process')
        login_url = reverse('uniauth_saml2_idp:login')+'?next={}'.format(login_process_url)

        # test a login
        login_data = dict(username='admin',
                          password='admin')
        # create a dummy user
        self.user = self._get_superuser_user()

        # agreement screen
        self._add_sp()
        self.sp = ServiceProvider.objects.first()
        self.sp.agreement_screen = 1
        self.sp.save()

        login_response = self.client.post(login_url, data=login_data, follow=True)
        assert 'has requested the following informations' in login_response.content.decode()

        self.sp.delete()
        self.user.delete()
