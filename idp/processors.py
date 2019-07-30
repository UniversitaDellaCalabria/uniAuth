import hashlib
import logging
import random

from django.conf import settings
from django.contrib.auth.models import Group
from uniauth.processors import (BaseProcessor,
                                NameIdBuilder)
from . unical_attributes_generator import UnicalAttributeGenerator


logger = logging.getLogger(__name__)


if 'ldap_peoples' in settings.INSTALLED_APPS:
    from ldap_peoples.models import LdapAcademiaUser

if 'multildap' in settings.INSTALLED_APPS:
    from multildap.client import LdapClient


class GroupProcessor(BaseProcessor):
    """
        Example implementation of access control for users:
        - superusers are allowed
        - staff is allowed
        - they have to belong to a certain group
    """
    group = "ExampleGroup"

    def has_access(self, user):
        return user.is_superuser or \
               user.is_staff or \
               user.groups.filter(name=self.group).exists()


class LdapAcademiaProcessor(BaseProcessor):
    """ Processor class used to retrieve attribute from LDAP server
        and user nameID (userID) with standard formats
    """

    def get_identity(self, user):
        return LdapAcademiaUser.objects.filter(eduPersonPrincipalName=user.username).first()


    def create_identity(self, user, sp={}):
        """ Generate an identity dictionary of the user based on the
            given mapping of desired user attributes by the SP
        """
        default_mapping = {'username': 'username'}
        sp_mapping = sp['config'].get('attribute_mapping',
                                      default_mapping)

        # get ldap user
        lu = self.get_identity(user)
        logging.info("{} doesn't have a valid computed ePPN in LDAP, please fix it!".format(user.username))
        results = {}
        for user_attr, out_attr in sp_mapping.items():
            if hasattr(user, user_attr):
                attr = getattr(user, user_attr)
                results[out_attr] = attr() if callable(attr) else attr

        if not lu:
            return results

        for user_attr, out_attr in sp_mapping.items():
            if hasattr(lu, user_attr):
                attr = getattr(lu, user_attr)
                results[out_attr] = attr() if callable(attr) else attr

        # add custom/legacy attribute made by processing
        results = self.extra_attr_processing(results, sp_mapping)

        # if targetedID is available give it to sp
        if self.eduPersonTargetedID:
            results['eduPersonTargetedID'] = [self.eduPersonTargetedID]

        return results


class LdapUnicalAcademiaProcessor(LdapAcademiaProcessor):
    """
    The same of its father but with a custom attribute processing
    for legacy support to stange SP
    """
    def extra_attr_processing(self, results, sp_mapping):
        return UnicalAttributeGenerator.process(results, sp_mapping)


class LdapUnicalMultiAcademiaProcessor(LdapUnicalAcademiaProcessor):
    """
    Uses pyMultiLDAP to gather an uid from multiple sources.
    It will stop on the first occurrence.
    """

    def get_identity(self, user):
        identity = None
        for lc in settings.LDAP_CONNECTIONS:
            ldapfilter = '(uid={})'.format(user.original_uid)
            logging.debug("Processor {} searches for {} in {}".format(self.__class__,
                                                                      user.username,
                                                                      lc))
            identity = lc.get(search=ldapfilter, format='object')
            if identity:
                return identity
