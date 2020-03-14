import defusedxml
import logging
import os
import json
import requests
import saml2.xmldsig

from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.module_loading import import_string

from . exceptions import NotYetImplemented


logger = logging.getLogger('__name__')


class AgreementRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    sp_entity_id = models.TextField()
    attrs = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # index field length problem
        # unique_together = ("user", "sp_entity_id")
        verbose_name = _('Agreement Record')
        verbose_name_plural = _('Agreement Records')

    def __str__(self):
        return '{}, {}'.format(self.user, self.created)

    def is_expired(self):
        valid_for = getattr(settings, "SAML_IDP_USER_AGREEMENT_VALID_FOR")
        if not valid_for:
            return False
        else:
            return timezone.now() > self.created + timedelta(hours=valid_for)

    def wants_more_attrs(self, newAttrs):
        return bool(set(newAttrs).difference(self.attrs.split(",")))


class ServiceProvider(models.Model):
    entity_id = models.CharField(max_length=254, unique=True)
    display_name = models.CharField(max_length=254)
    metadata_url = models.URLField(max_length=254, blank=True, default='',
                                   help_text=_("optional, usually this "
                                               "is the same of entityID"))
    description = models.TextField(blank=True, default='')
    agreement_screen = models.BooleanField(default=settings.SAML_IDP_SHOW_USER_AGREEMENT_SCREEN)
    agreement_consent_form = models.BooleanField(default=settings.SAML_IDP_SHOW_CONSENT_FORM)
    agreement_message = models.TextField(blank=True, default='')
    signing_algorithm = models.CharField(choices=[(y,x) for x,y in saml2.xmldsig.SIG_ALLOWED_ALG],
                                         default=settings.SAML_AUTHN_SIGN_ALG,
                                         max_length=256)
    digest_algorithm = models.CharField(choices=[(y,x) for x,y in saml2.xmldsig.DIGEST_ALLOWED_ALG],
                                        default=settings.SAML_AUTHN_DIGEST_ALG,
                                        max_length=256)
    disable_encrypted_assertions = models.BooleanField(default=True,
                                                       help_text=('disable encryption'))
    attribute_processor = models.CharField(default=settings.DEFAULT_SPCONFIG['processor'],
                                           help_text=_('"package.file.classname", '
                                                       'example: "idp.processors.LdapAcademiaProcessor"'),
                                           max_length=256, blank=True)
    attribute_mapping = models.TextField(default=json.dumps(settings.DEFAULT_SPCONFIG['attribute_mapping'],
                                                            sort_keys=True,
                                                            indent=4),
                                         blank=True, null=True,
                                         help_text=_('Attribute that would be release to this SP, in JSON format.'))
    force_attribute_release = models.BooleanField(default=False,
                                                   help_text=_("Release the configured attribute mapping "
                                                               "regardless of what SP asks for."))
    is_valid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True,null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Service Provider')
        verbose_name_plural = _('Service Providers')

    def __str__(self):
        return '{}'.format(self.entity_id)

    def validate(self):
        error = None
        try:
            # check if class Processor exists and is importable
            import_string(self.attribute_processor)
        except Exception as e:
            error = '{}'.format(e)
            self.is_active = False

        try:
            # check if mapping is a real dict or
            # if it have syntax errors (try json.loads).
            # Dict must do not have a trailing "," at last element
            json.loads(self.attribute_mapping)
        except Exception as e:
            error = 'Attribute Mapping is not a valid JSON format: {}'.format(e)
            self.is_active = False

        # test if its entityID is available in metadatastore
        try:
            get_idp_config = import_string('uniauth.utils.get_idp_config')
            get_idp_config().metadata.service(self.entity_id,
                                              "spsso_descriptor",
                                              'assertion_consumer_service')
        except Exception as e:
            error = '{} is not present in any Metadata'.format(e)
            self.is_active = False

        if error:
            self.is_valid = self.is_active
            self.save()
            raise Exception(error)

        self.is_valid = True
        self.save()
        return self.is_valid

    @classmethod
    def as_idpspconfig_dict(cls):
        d = dict()
        for entity in cls.objects.filter(is_active=True):
            d[entity.entity_id] = entity.as_idpspconfig_dict_element()
        return d

    def as_idpspconfig_dict_element(self):
        d = {'processor': self.attribute_processor,
             'attribute_mapping': json.loads(self.attribute_mapping),
             'force_attribute_release': self.force_attribute_release,
             'display_name': self.display_name,
             'display_description': self.description,
             'display_agreement_message': self.agreement_message,
             'signing_algorithm': self.signing_algorithm,
             'digest_algorithm': self.digest_algorithm,
             'disable_encrypted_assertions': self.disable_encrypted_assertions,
             'show_user_agreement_screen': self.agreement_screen,
             'display_agreement_consent_form': self.agreement_consent_form}
        return d


class MetadataStore(models.Model):
    MDStype = (('remote', 'remote'),
               ('mdq', 'mdq'),
               ('local', 'local'))

    name = models.CharField(max_length=256)
    url = models.CharField(max_length=255,
                           blank=True, null=True,
                           help_text=_('for "remote" and "mdq", '
                                       'use path if "local".'))
    file = models.FileField(blank=True, null=True,
                            upload_to='metadata',
                            help_text=_('https cert if type==mdq '
                                        'https cert if type==remote '
                                        'xml file if type==file'))
    type = models.CharField(choices=MDStype, max_length=12)
    kwargs = models.TextField(help_text=_("A dictionary"), default='{}')
    is_valid = models.BooleanField(default=False,
                                   help_text=_('if sign validation was succesfull'))
    is_active = models.BooleanField(default=False, help_text=_('enable/disable this metadata source'))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True,null=True, blank=True,
                                   help_text=_('when last download/validation occourred'))

    class Meta:
        verbose_name = _('Metadata Store')
        verbose_name_plural = _('Metadatas Store')

    @classmethod
    def as_pysaml_mdstore_dict(cls):
        """
        returns something like
            {
            'local': [
                     (os.path.join(IDP_SP_METADATA_PATH, 'sp_metadata.xml'),),
                     (os.path.join('/path/to/somewher',),),
                     ],
            "remote": [{
                "url": 'https://satosa.testunical.it/Saml2/metadata',
                "cert": "/opt/satosa-saml2/pki/frontend.cert",
                "disable_ssl_certificate_validation": True,
                 }],
            "mdq": [{
                "url": "https://ds.testunical.it",
                "cert": "certficates/others/ds.testunical.it.cert",
                }]
            }
        """
        stores = cls.objects.filter(is_active=True, is_valid=True)
        d = {}
        for store in stores:
            if not d.get(store.type):
                d[store.type] = []
            d[store.type].append(store.as_pysaml2_mdstore_row())
        return d

    def as_pysaml2_mdstore_row(self):
        if self.type in ('remote', 'mdq'):
            d = dict(url=self.url)
            if self.file: d['cert'] = self.file.path
            if self.kwargs:
                kwargs = json.loads(self.kwargs)
                d.update(kwargs)
            return d
        elif self.type == 'local':
            return (self.url) if not self.file else (self.file.path)
        raise NotYetImplemented('see models.MetadataStore.as_pysaml2_mdstore_row')

    def validate(self):
        error = None
        if self.type in ('remote', 'mdq'):
            if self.url:
                try:
                    r = requests.head(self.url + '/entities/')
                    if r.status_code != 200:
                        logger.error('{} /entities query failed: {}'.format(self, r.content))
                        self.is_active = False
                except Exception as e:
                    error = 'Endpoint is not reachable: {}'.format(e)
                    self.is_active = False

        elif self.type == 'local':
            # check that is a valid XML file, avoids: pysaml2 Exception on parse
            try:
                if self.file:
                    defusedxml.ElementTree.fromstring(open(self.file.path).read())
                if self.url:
                    files = [os.path.join(self.url, f) for f in os.listdir(self.url)]
                    for f in files:
                        defusedxml.ElementTree.fromstring(open(f).read())
            except Exception as e:
                self.is_active = False
                error = 'found an invalid XML: {}'.format(e)

            res = (self.url) if not self.file else (self.file.path)
            if not os.path.exists(res):
                self.is_active = False
                error = 'Path is not existent: {}'.format(res)

        try:
            json.loads(self.kwargs)
        except Exception as e:
            self.is_active = False
            error = "kwargs JSON format error: {}".format(e)

        if error:
            self.is_valid = self.is_active
            self.save()
            raise Exception(error)

        self.is_valid = True
        self.save()
        return self.is_valid

    # TODO
    # def save(...
    # validate content otherwise save it as is_valid = False

    def __str__(self):
        return '{} [{}]'.format(self.name, self.is_valid)
