import base64
import copy
import xml.dom.minidom
import xml.etree.ElementTree
import zlib

from django.conf import settings
from saml2.config import IdPConfig
from saml2.server import Server
from xml.parsers.expat import ExpatError

from . exceptions import (MetadataNotFound,
                          MetadataCorruption,
                          SPConfigurationMissing)
from . models import MetadataStore, ServiceProvider


def repr_saml(saml_str, b64=False):
    """ Decode SAML from b64 and b64 deflated and
        return a pretty printed representation
    """
    try:
        msg = base64.b64decode(saml_str).decode() if b64 else saml_str
        dom = xml.dom.minidom.parseString(msg)
    except (UnicodeDecodeError, ExpatError):
        # in HTTP-REDIRECT the base64 must be inflated
        msg = base64.b64decode(saml_str)
        inflated = zlib.decompress(msg, -15)
        dom = xml.dom.minidom.parseString(inflated.decode())
    return dom.toprettyxml()


def encode_http_redirect_saml(saml_envelope):
    return base64.b64encode(zlib.compress(saml_envelope.encode()))


def get_idp_config(saml_idp_config=settings.SAML_IDP_CONFIG):
    conf = IdPConfig()
    idp_config = copy.deepcopy(saml_idp_config)

    # this is only used for merge DB metadatastores configurations
    db_mdstores = MetadataStore.as_pysaml_mdstore_dict()
    for k,v in db_mdstores.items():
        if not idp_config['metadata'].get(k):
            idp_config['metadata'][k] = []
        for endpoint in v:
            if endpoint not in idp_config['metadata'][k]:
                idp_config['metadata'][k].append(endpoint)
    # end DB metadatastores configurations
    try:
        conf.load(idp_config)
    except FileNotFoundError as e:
        raise MetadataNotFound(e)
    except xml.etree.ElementTree.ParseError as e:
        raise SPConfigurationMissing(e)
    except Exception as e:
        raise Exception(e)
    return Server(config=conf)


def get_idp_sp_config():
    idp_sp_config = settings.SAML_IDP_SPCONFIG
    idp_sp_config_db = ServiceProvider.as_idpspconfig_dict()
    idp_sp_config.update(idp_sp_config_db)
    return idp_sp_config


def get_client_id(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    ua = request.META.get('HTTP_USER_AGENT', '')
    return '{} ({})'.format(ip, ua)
