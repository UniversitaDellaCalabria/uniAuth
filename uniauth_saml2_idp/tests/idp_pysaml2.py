import os
import saml2
from saml2 import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
)
from saml2.entity_category import refeds, edugain
from saml2.saml import NAMEID_FORMAT_TRANSIENT, NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAME_FORMAT_URI


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGIN_URL = "/idp/login/"

# idp protocol:fqdn:port
HOST = "localhost"
PORT = 9000  # None if 80 or 443...
HTTPS = False

BASE = "https://{}".format(HOST) if HTTPS else "http://{}".format(HOST)
if PORT:
    BASE += ":{}".format(PORT)

BASE_URL = "{}/idp".format(BASE)
# end

IDP_SP_METADATA_PATH = "tests/data/metadata"

# please check [Refactor datetime](https://github.com/IdentityPython/pysaml2/pull/518)
# only used to parse issue_instant in a try...
SAML2_DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%SZ", "%Y%m%d%H%M%SZ"]

SAML_IDP_CONFIG = {
    "debug": True,
    # "xmlsec_binary": get_xmlsec_binary(["/opt/local/bin", "/usr/bin/xmlsec1"]),
    "entityid": "%s/metadata" % BASE_URL,
    "entity_category_support": [
        edugain.COCO,  # "http://www.geant.net/uri/dataprotection-code-of-conduct/v1"
        refeds.RESEARCH_AND_SCHOLARSHIP,
    ],
    "attribute_map_dir": "data/attribute-maps",
    "description": "SAML2 IDP",
    "service": {
        "idp": {
            "name": "Django testunical SAML IdP",
            "ui_info": {
                "display_name": [
                    {"lang": "en", "text": "Unical IdP"},
                    {"lang": "it", "text": "Unical IdP"},
                ],
                "description": [
                    {"lang": "en", "text": "University of Calabria Identity Provider"},
                    {
                        "lang": "it",
                        "text": "Identity Provider della Università della Calabria",
                    },
                ],
                "information_url": {
                    "lang": "it",
                    "text": "https://www.unical.it/portale/strutture/centri/centroict/schdeserviziict/idem/",
                },
                "privacy_statement_url": {
                    "lang": "it",
                    "text": "https://www.unical.it/portale/ateneo/privacy/",
                },
                "logo": {
                    "width": "80",
                    "height": "60",
                    "text": "https://{}/static/img/logo.svg".format(HOST),
                },
            },
            "endpoints": {
                "single_sign_on_service": [
                    ("%s/sso/post" % BASE_URL, BINDING_HTTP_POST),
                    ("%s/sso/redirect" % BASE_URL, BINDING_HTTP_REDIRECT),
                ],
                "single_logout_service": [
                    ("%s/slo/post" % BASE, BINDING_HTTP_POST),
                    # ("%s/slo/redirect" % BASE, BINDING_HTTP_REDIRECT)
                ],
            },
            # transient per default, persistent if asked by sp
            "name_id_format": [NAMEID_FORMAT_TRANSIENT, NAMEID_FORMAT_PERSISTENT],
            "validate_certificate": True,
            # this is default
            "only_use_keys_in_metadata": True,
            "want_authn_requests_only_with_valid_cert": True,
            "want_authn_requests_signed": True,
            "logout_requests_signed": True,
            "sign_response": True,
            "sign_assertion": True,
            # the following if set should be a cert filename, not a boolean
            # 'verify_ssl_cert': None,
            # 'verify_encrypt_cert_assertion': None,
            # 'verify_encrypt_cert_advice': None,
            # this works if pysaml2 is installed from peppelinux's fork
            # 'signing_algorithm':  saml2.xmldsig.SIG_RSA_SHA256,
            # 'digest_algorithm':  saml2.xmldsig.DIGEST_SHA256,
            "policy": {
                "default": {
                    "lifetime": {"minutes": 15},
                    # if the sp are not conform to entity_categories (in our metadata) the attributes will not be released
                    # "entity_categories": ["refeds", "edugain"],
                    # "entity_categories": ["refeds",],
                    "name_form": NAME_FORMAT_URI,
                    # global pysaml2 restrictions, useless with custom AttributeProcessors
                    # "attribute_restrictions": {
                    # 'username': None,
                    # 'first_name': None,
                    # 'last_name': None,
                    #
                    # Here only mail addresses that end with ".umu.se" will be returned.
                    # 'email': None,
                    # #'email': [".*\.umu\.se$"],
                    # "mail": [".*\.umu\.se$"],
                    # },
                },
                # attributes will be released only if this SP have refeds in out entity_categories in its metadata.
                # "https://sp1.testunical.it/saml2/metadata/": {
                # "entity_categories": ["refeds",]
                # }
                # "https://example.com/sp": {
                # "lifetime": {"minutes": 5},
                # "nameid_format": NAMEID_FORMAT_PERSISTENT,
                # "name_form": NAME_FORMAT_BASIC
                # }
            },
        },
        # TODO
        # AttributeAuthorityDescriptor is needed for legacy SP
        # this adds the needed attributes in metadata ...!
        # 'aq': {
        #
        #    }
    },
    # Quite useless, you can even configure metadata store through admin backend!
    "metadata": {
        # 'local': [
        # IDP_SP_METADATA_PATH,
        # ],
        #
        # "remote": [{
        # "url": 'https://satosa.testunical.it/Saml2/metadata',
        # "cert": "/opt/satosa-saml2/pki/frontend.cert",
        # working only with pplx-dev fork:
        # "disable_ssl_certificate_validation": True,
        # }],
        # "mdq": [{
        # "url": "http://localhost:8001",
        # "url": "https://ds.testunical.it",
        # "cert": "certficates/others/ds.testunical.it.cert",
        # working only with pplx-dev fork:
        # "disable_ssl_certificate_validation": True,
        # }]
    },
    # Signing
    "key_file": BASE_DIR + "/tests/data/certificates/private.pem",
    "cert_file": BASE_DIR + "/tests/data/certificates/public.pem",
    # Encryption
    "encryption_keypairs": [
        {
            "key_file": BASE_DIR + "/tests/data/certificates/private.pem",
            "cert_file": BASE_DIR + "/tests/data/certificates/public.pem",
        }
    ],
    # How many hours this configuration is expected to be accurate as eposed in metadata
    # 'valid_for': 24 * 10,
    # own metadata settings
    "contact_person": [
        {
            "given_name": "Giuseppe",
            "sur_name": "De Marco",
            "company": "Universita della Calabria",
            "email_address": "giuseppe.demarco@unical.it",
            "contact_type": "administrative",
        },
        {
            "given_name": "Giuseppe",
            "sur_name": "De Marco",
            "company": "Universita della Calabria",
            "email_address": "giuseppe.demarco@unical.it",
            "contact_type": "technical",
        },
    ],
    # you can set multilanguage information here
    "organization": {
        "name": [("Unical", "it"), ("Unical", "en")],
        "display_name": [("Unical", "it"), ("Unical", "en")],
        "url": [("http://www.unical.it", "it"), ("http://www.unical.it", "en")],
    },
    # TODO: put idp logs in a separate file too
    # "logger": {
    # "rotating": {
    # "filename": "idp.log",
    # "maxBytes": 500000,
    # "backupCount": 5,
    # },
    # "loglevel": "debug",
    # }
}

SAML_IDP_SHOW_USER_AGREEMENT_SCREEN = True
SAML_IDP_SHOW_CONSENT_FORM = False
SAML_IDP_USER_AGREEMENT_ATTR_EXCLUDE = []
# User agreements will be valid for 1 year unless overriden. If this attribute is not used, user agreements will not expire
SAML_IDP_USER_AGREEMENT_VALID_FOR = 24 * 365

SAML_IDP_DJANGO_USERNAME_FIELD = "username"
# alg, salt and arguments used for computed user identifier used in opaque, transient and persistent nameid_format
SAML_COMPUTEDID_HASHALG = "sha256"
SAML_COMPUTEDID_SALT = b"87sdfybDSFDSFsdf__7yb"

SAML_AUTHN_SIGN_ALG = saml2.xmldsig.SIG_RSA_SHA256
SAML_AUTHN_DIGEST_ALG = saml2.xmldsig.DIGEST_SHA256

# Encrypt authn response by default (will not work with SP that doesn't have enc keys in their metadata)
SAML_FORCE_ENCRYPTED_ASSERTION = False

# if enabled and nameid format is persistent the nameid related to user:recipient_id will be stored in PersistentId model
SAML_ALLOWCREATE = True

# SP configurations
SAML_IDP_SPCONFIG = {}

# Disable unconfigured SP even if they are in MetadataStore
SAML_DISALLOW_UNDEFINED_SP = False

# This coniguration will be used by default for each newly created SP through admin backend.
DEFAULT_SPCONFIG = {
    "processor": "uniauth_saml2_idp.processors.base.BaseProcessor",
    "attribute_mapping": {
        "uid": "uid",
        "persistent_ids": "persistent_ids",
        "email": "email",
        "first_name": "first_name",
        "last_name": "last_name",
        "username": "username",
        # 'is_staff': 'is_staff',
        # 'is_superuser':  'is_superuser',
        # refeds + edugain Entities
        # "cn": "cn",
        # "eduPersonEntitlement": "eduPersonEntitlement",
        # "eduPersonPrincipalName": "eduPersonPrincipalName",
        # "schacHomeOrganization": "schacHomeOrganization",
        # "eduPersonHomeOrganization": "eduPersonHomeOrganization",
        # "eduPersonAffiliation": "eduPersonAffiliation",
        # "eduPersonScopedAffiliation": "eduPersonScopedAffiliation",
        # "eduPersonTargetedID": "eduPersonTargetedID",
        # "mail": ["mail", "email"],
        # "email": ["mail", "email"],
        # "schacPersonalUniqueCode": "schacPersonalUniqueCode",
        # "schacPersonalUniqueID": "schacPersonalUniqueID",
        # "sn": "sn",
        # "givenName": ["givenName", "another_possible_occourrence"],
        # "displayName": "displayName",
        # custom attributes
        # "codice_fiscale": "codice_fiscale",
        # "matricola_studente": "matricola_studente",
        # "matricola_dipendente": "matricola_dipendente"
    },
    "display_name": "Unical SP",
    "display_description": "This is for test purpose",
    # Only for SP externals to our organization
    "display_agreement_message": "Some information about you has been requested",
    "signing_algorithm": saml2.xmldsig.SIG_RSA_SHA256,
    "digest_algorithm": saml2.xmldsig.DIGEST_SHA256,
    "disable_encrypted_assertions": True,
    # 'show_user_agreement_screen': SAML_IDP_SHOW_USER_AGREEMENT_SCREEN
}

# Quite useless, you can even configure SP through admin backend!
# shibboleth test SP
# SAML_IDP_SPCONFIG['https://sp.testunical.it/shibboleth'] = DEFAULT_SPCONFIG
# SAML_IDP_SPCONFIG['https://sp1.testunical.it/saml2/metadata/'] = DEFAULT_SPCONFIG

# satosa frontend
# SAML_IDP_SPCONFIG['https://satosa.testunical.it/Saml2/metadata'] = DEFAULT_SPCONFIG
