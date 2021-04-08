import hashlib

from django.conf import settings
from saml2.saml import (NAMEID_FORMAT_UNSPECIFIED,
                        NAMEID_FORMAT_TRANSIENT,
                        NAMEID_FORMAT_PERSISTENT,
                        NAMEID_FORMAT_EMAILADDRESS,
                        NAMEID_FORMAT_X509SUBJECTNAME,
                        NAMEID_FORMAT_WINDOWSDOMAINQUALIFIEDNAME,
                        NAMEID_FORMAT_KERBEROS,
                        NAMEID_FORMAT_ENTITY,
                        NAMEID_FORMAT_ENCRYPTED)


class NameIdBuilder:
    """ Processor with methods to retrieve nameID standard format
        see: https://wiki.shibboleth.net/confluence/display/CONCEPT/NameIdentifiers

        also: http://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf
    """

    # None needs to be implemented
    format_mappings = {NAMEID_FORMAT_UNSPECIFIED: 'get_nameid_unspecified',
                       NAMEID_FORMAT_TRANSIENT: 'get_nameid_transient',
                       NAMEID_FORMAT_PERSISTENT: 'get_nameid_persistent',
                       NAMEID_FORMAT_EMAILADDRESS: 'get_nameid_email',
                       # TODO: need to be implemented
                       NAMEID_FORMAT_X509SUBJECTNAME: None,
                       NAMEID_FORMAT_WINDOWSDOMAINQUALIFIEDNAME: None,
                       NAMEID_FORMAT_KERBEROS: None,
                       NAMEID_FORMAT_ENTITY: None,
                       NAMEID_FORMAT_ENCRYPTED: None}

    @staticmethod
    def get_nameid_prefix(user_id, sp_entityid, idp_entityid='', user=''):
        """ Inherit and customize as your needs"""
        return '!'.join((idp_entityid, sp_entityid, user_id))

    @classmethod
    def get_nameid_opaque(cls, user_id,
                          salt=settings.SAML_COMPUTEDID_SALT, **kwargs):
        """ Returns opaque salted unique identifiers
        """
        salted_value = user_id.encode()+salt
        alg = getattr(hashlib, settings.SAML_COMPUTEDID_HASHALG)
        opaque = alg(salted_value)
        return opaque.hexdigest()

    @classmethod
    def get_nameid_persistent(cls, user_id,
                              sp_entityid='', idp_entityid='',
                              user=None):
        """ Get PersistentID
            TransientID format as ComputedID
            see: http://software.internet2.edu/eduperson/internet2-mace-dir-eduperson-201602.html#eduPersonTargetedID
        """

        #
        # TODO allowCreate and store every newly created computedID if persistentID is True
        #

        pid = user.persistent_id(sp_entityid)
        if user and not pid:
            # computed
            user_persistent_id = cls.get_nameid_opaque(cls.get_nameid_prefix(user_id,
                                                                             sp_entityid,
                                                                             idp_entityid,
                                                                             user),
                                                       salt=settings.SAML_COMPUTEDID_SALT)
        else:
            user_persistent_id = pid
        return user_persistent_id

    @classmethod
    def get_nameid_email(cls, user_id, user=None, **kwargs):  # pragma: no cover
        return user.email

    @classmethod
    def get_nameid_transient(cls, user_id, sp_entityid='', **kwargs):
        """ This would an opaque and reusable
        """
        return cls.get_nameid_opaque(cls.get_nameid_prefix(user_id,
                                                           sp_entityid,
                                                           kwargs.get(
                                                               'idp_entityid', ''),
                                                           kwargs.get('user', '')),
                                     salt=settings.SAML_COMPUTEDID_SALT)

    @classmethod
    def get_nameid_unspecified(cls, user_id, **kwargs):
        """ returns user_id as is
        """
        return user_id  # pragma: no cover

    @classmethod
    def get_nameid(cls, user_id, nameid_format, **kwargs):
        method = cls.format_mappings.get(nameid_format)
        if not method:  # pragma: no cover
            raise NotImplementedError('{} was not been mapped in '
                                      'NameIdBuilder.format_mappings'.format(nameid_format))
        if not hasattr(cls, method):  # pragma: no cover
            raise NotImplementedError('{} was not been implemented '
                                      'NameIdBuilder methods'.format(nameid_format))
        name_id = getattr(cls, method)(user_id, **kwargs)
        return name_id


class BaseProcessor:
    """ Processor class is used to determine if a user has access to a
        client service of this IDP
        and to construct the identity dictionary which is sent to the SP
    """

    def __init__(self, entity_id, request=None):
        self._entity_id = entity_id
        self.eduPersonTargetedID = None
        self.request = request

    def has_access(self, request):
        """ Check if this user is allowed to use this IDP
        """
        return True

    def enable_multifactor(self, user):
        """ Check if this user should use a second authentication system
        """
        return False

    def get_user_id(self, user, sp, idp_config):
        """ Get identifier for a user. Take the one defined in
            settings.SAML_IDP_DJANGO_USERNAME_FIELD first, if not set
            use the USERNAME_FIELD property which is set on the
            user Model. This defaults to the user.username field.
        """
        user_field_str = sp['config'].get('nameid_field') or \
            getattr(settings, 'SAML_IDP_DJANGO_USERNAME_FIELD', None) or \
            getattr(user, 'USERNAME_FIELD', 'username')

        if not hasattr(user, user_field_str):  # pragma: no cover
            raise ValueError(
                'user doesn\'t have {} as attribute'.format(user_field_str))

        user_field = getattr(user, user_field_str)

        if callable(user_field):
            user_uid = str(user_field())
        else:
            user_uid = str(user_field)

        # returns in a real name_id format
        user_id = NameIdBuilder.get_nameid(user_uid,
                                           sp['name_id_format'],
                                           sp_entityid=sp['id'],
                                           idp_entityid=idp_config.entityid,
                                           user=user)
        # needed for targetedID attr
        if sp['name_id_format'] in [NAMEID_FORMAT_PERSISTENT,
                                    NAMEID_FORMAT_TRANSIENT]:
            self.eduPersonTargetedID = user_id
        return user_id

    def extra_attr_processing(self, results, sp_mapping, **kwargs):
        """This should inherits another class
           and be executed in create_identity
        """
        return results

    def process_attributes(self, user, sp_mapping):
        results = {}
        for user_attr, out_attr in sp_mapping.items():
            if not isinstance(out_attr, list):
                out_attr = [out_attr]
            for item in out_attr:
                if hasattr(user, item):
                    attr = getattr(user, item)
                    results[user_attr] = attr() if callable(attr) else attr
                    break
        return results

    def create_identity(self, user, sp={}):
        """ Generate an identity dictionary of the user based on the
            given mapping of desired user attributes by the SP
        """
        default_mapping = {'username': 'username'}
        sp_mapping = sp['config'].get('attribute_mapping', default_mapping)

        results = self.process_attributes(user, sp_mapping)
        results = self.extra_attr_processing(results, sp_mapping)
        return results
