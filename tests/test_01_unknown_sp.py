import copy
import os
import logging
import re
import requests
import sys

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
from .idp_pysaml2 import SAML_IDP_CONFIG

from .sp.sp_pysaml2 import (SAML_CONFIG as SAML_SP_CONFIG,
                            BASE_URL,
                            BASE_DIR)
from uniauth.views import *
from uniauth.utils import (repr_saml,
                           get_idp_config,
                           get_idp_sp_config,
                           get_client_id)


logger = logging.getLogger('django_test')


# clean up sp metadata folder
mds = ['tests/sp/metadata/idp.xml', 'tests/data/metadata/sp.xml']

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

def extract_saml_authn_data(result):
    url = reverse('uniauth:saml_login_binding', kwargs={'binding': 'POST'})
    logging.info('IdP Target is: {}'.format(url))
    # url = re.search(action_post_regexp, result.get('data', '')).groupdict()['value']
    data = {'SAMLRequest': re.search(samlrequest_form_regexp,
                                     result.get('data', ''))\
                              .groupdict()['value']}
    return url, data


class TestUnknowRP(TestCase):
    def setUp(self):
        # put idp metadata in sp metadata store
        # self.IDP = IdPConfig()
        # self.IDP.load(copy.deepcopy(SAML_IDP_CONFIG))
        # idp_metadata = entity_descriptor(self.IDP)
        cleanup_metadata()
        idp_md_url = reverse('uniauth:saml2_idp_metadata')
        client = Client()
        idp_metadata = client.get(idp_md_url)

        with open(mds[0], 'wb') as fd:
            fd.write(idp_metadata.content)

        # create a pysaml SP
        self.sp_conf = SPConfig()
        self.sp_conf.load(copy.deepcopy(SAML_SP_CONFIG))

        self.sp_client = Saml2Client(self.sp_conf)
        logger.info('{} SP: {}'.format(self.__class__.__name__,
                                       self.client))

    def test_authn_request(self):
        session_id, result = self.sp_client.prepare_for_authenticate(
                                             entityid=idp_eid,
                                             relay_state='/',
                                             binding=BINDING_HTTP_POST,
                                             )
                                             #sign=False,
                                             #sigalg=None)

        url, data = extract_saml_authn_data(result)
        
        client = Client()
        response = client.post(url, data)

        assert response.status_code == 403 and \
               'Incorrectly signed' in response.content.decode()
        logging.info('IdP do not accept SP with unknow metadata -> OK')