from django.conf import settings
from django.urls import reverse
from django.test import override_settings

from .base import BINDING_HTTP_POST, BaseTestRP, extract_saml_authn_data, idp_eid


class TestRP(BaseTestRP):
    def setUp(self):
        super().setUp()
        self._superuser_login()
        self._add_sp_md()

    def test_unsigned_authn_request(self):
        """
        a UNsigned saml request from a well know SP
        """
        value = settings.SAML_IDP_CONFIG
        value["service"]["idp"]["want_authn_requests_signed"] = True
        with override_settings(SAML_IDP_CONFIG=value):
            session_id, result = self.sp_client.prepare_for_authenticate(
                entityid=idp_eid,
                relay_state="/",
                binding=BINDING_HTTP_POST,
                sign=False,
                sigalg=None,
            )
            url, data = extract_saml_authn_data(result)
            response = self.client.post(url, data)

            # forbidden !
            assert (
                response.status_code == 403
                and "Incorrectly signed" in response.content.decode()
            )

    def test_authn_request(self):
        """
        a signed saml request from a well know SP
        """
        url, data, session_id = self._get_sp_authn_request()

        response = self.client.post(url, data)

        login_url = reverse("uniauth_saml2_idp:saml_login_process")
        assert response.status_code == 302 and response.url == login_url
