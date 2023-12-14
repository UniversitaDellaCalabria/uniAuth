
from django.conf import settings
from uniauth_saml2_idp.models import ServiceProvider
from .base import BaseTestRP, login_url


class TestEnabledRP(BaseTestRP):
    def setUp(self):
        super().setUp()
        self._add_sp_md()
        settings.SAML_DISALLOW_UNDEFINED_SP = True
        self._add_sp()
        self.sp = ServiceProvider.objects.first()
        self.login_data = dict(username="admin", password="admin")
        # create a dummy user
        self.user = self._get_superuser_user()

    def test_faulty_attr_processor(self):
        self.sp.attribute_processor = "uniauth_saml2_idp.processors.base.UNKNOW"
        self.sp.save()

        url, data, session_id = self._get_sp_authn_request()

        response = self.client.post(url, data, follow=True)
        login_response = self.client.post(
            login_url, data=self.login_data, follow=True)
        assert b"AttributeError" in login_response.content
