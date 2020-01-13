import copy
import os
import logging
import re
import requests
import sys
import subprocess


from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.config import SPConfig, IdPConfig
from saml2.client import Saml2Client
from saml2.metadata import entity_descriptor
from saml2.response import AuthnResponse
from saml2.s_utils import (UnknownPrincipal,
                           UnsupportedBinding,
                           UnknownSystemEntity)

sys.path.append(os.getcwd())
from .idp_pysaml2 import SAML_IDP_CONFIG, IDP_SP_METADATA_PATH

from .sp.sp_pysaml2 import (SAML_CONFIG as SAML_SP_CONFIG,
                            BASE_URL,
                            BASE_DIR)
from uniauth.views import *
from uniauth.utils import (get_idp_config,
                           get_idp_sp_config,
                           get_client_id,
                           repr_saml)


logger = logging.getLogger('django_test')


# clean up sp metadata folder
idp_md_path = 'tests/data/metadata'
sp_md_path = 'tests/sp/metadata'
mds = [sp_md_path+'/idp.xml', idp_md_path+'/sp.xml']
for md_path in (idp_md_path, sp_md_path):
    if not os.path.exists(md_path):
        os.mkdir(md_path)


def cleanup_metadata():
    for md in mds:
        if os.path.exists(md):
            os.remove(md)

idp_eid = SAML_IDP_CONFIG['entityid']
sp_eid = SAML_SP_CONFIG['entityid']

action_post_regexp =('(?P<name>action)='
                     '"(?P<value>[a-zA-Z0-9\.\:\/\_\?\=]*)"')
samlrequest_form_regexp = ('.*name="SAMLRequest" '
                           'value="(?P<value>[a-zA-Z0-9=+]*)"[\s\n.]*')

samlresponse_form_regexp = 'name="SAMLResponse" value="(?P<value>[a-zA-Z0-9+=]*)"'
login_process_url = reverse('uniauth:saml_login_process')
login_url = reverse('uniauth:login')+'?next={}'.format(login_process_url)


def extract_saml_authn_data(result):
    url = reverse('uniauth:saml_login_binding', kwargs={'binding': 'POST'})
    logging.info('IdP Target is: {}'.format(url))
    # url = re.search(action_post_regexp, result.get('data', '')).groupdict()['value']
    data = {'SAMLRequest': re.search(samlrequest_form_regexp,
                                     result.get('data', ''))\
                              .groupdict()['value']}
    return url, data


class BaseTestRP(TestCase):
    def setUp(self):
        # put idp metadata in sp metadata store
        # self.IDP = IdPConfig()
        # self.IDP.load(copy.deepcopy(SAML_IDP_CONFIG))
        # idp_metadata = entity_descriptor(self.IDP)
        cleanup_metadata()
        idp_md_url = reverse('uniauth:saml2_idp_metadata')
        client = Client()
        idp_metadata = client.get(idp_md_url)

        # idp metadata into sp md store
        with open(mds[0], 'wb') as fd:
            fd.write(idp_metadata.content)

        # create a pysaml SP
        self.sp_conf = SPConfig()
        self.sp_conf.load(copy.deepcopy(SAML_SP_CONFIG))

        self.sp_client = Saml2Client(self.sp_conf)
        logger.info('{} SP: {}'.format(self.__class__.__name__,
                                       self.client))

    def _get_superuser_user(self):
        data = dict(username='admin',
                    email='test@test.org',
                    is_superuser=1,
                    is_staff=1)
        user = get_user_model().objects.get_or_create(**data)[0]
        user.set_password('admin')
        user.save()
        return user

    def _superuser_login(self):
        user = self._get_superuser_user()
        self.client.force_login(user)

    def _add_sp_md(self):
        self._superuser_login()
        # put md store through admin UI
        create_url = reverse('admin:uniauth_metadatastore_add')
        data = dict(name='sptest',
                    type='local',
                    url=idp_md_path,
                    kwargs='{}',
                    is_active=1)
        response = self.client.post(create_url, data, follow=True)
        assert 'was added successfully' in response.content.decode()

        # put sp metadata into IDP md store
        sp_metadata = entity_descriptor(self.sp_conf)
        with open(IDP_SP_METADATA_PATH+'/sp.xml', 'wb') as fd:
            fd.write(sp_metadata.to_string())

    def _add_sp(self):
        self._superuser_login()
        create_url = reverse('admin:uniauth_serviceprovider_add')
        data = dict(entity_id = SAML_SP_CONFIG['entityid'],
                    display_name = 'That SP display name',
                    signing_algorithm = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
                    digest_algorithm = "http://www.w3.org/2001/04/xmlenc#sha256",
                    disable_encrypted_assertions=1,
                    is_active=1)
        response = self.client.post(create_url, data, follow=True)
        assert 'was added successfully' in response.content.decode()

    def _get_sp_authn_request(self):
        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST)
        url, data = extract_saml_authn_data(result)
        return url, data

    def _run_ldapd(self):
        self.ldapd = subprocess.Popen(["python3","tests/ldapd.py"])
