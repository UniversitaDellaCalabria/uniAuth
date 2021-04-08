import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.conf import settings

from ldap3.utils import conv


logger = logging.getLogger(__name__)


class LdapUnicalMultiAcademiaAuthBackend(ModelBackend):
    """
    This class logout a user if another session of that user
    will be created

    in settings.py
    AUTHENTICATION_BACKENDS = ['idp.multildap_auth.LdapUnicalMultiAcademiaAuthBackend',
                              ]
    """

    def authenticate(self, request, username=None, password=None):
        logger.info("--- LDAP BIND to MultiLDAP proxy ---")

        user = None
        lu = None
        dn = None

        username = conv.escape_filter_chars(username, encoding=None)
        for lc in settings.LDAP_CONNECTIONS:
            search_filter = '(uid={})'.format(username)
            lu = lc.get(search=search_filter)
            if lu:
                logger.info(
                    "--- LDAP search filter {} ---".format(search_filter))
                break

        if not lu:
            logger.info("--- LDAP BIND failed for {} ---".format(username))
            return None

        dn = list(lu.keys())[0]
        lu_obj = lc._as_object(lu)

        # check if username exists and if it is active
        if not lc.authenticate(dn, password):
            msg = "--- LDAP user {} seems to be unable to Auth to {} ---"
            logger.info(msg.format(dn, lc))
            return None
        else:
            msg = "--- LDAP user {} succesfully authenticated to {} ---"
            logger.info(msg.format(dn, lc))
            attrs = ','.join([i for i in list(lu.values())[0]])
            logger.info("--- LDAP user attributes: [{}]".format(attrs))
        username = lu_obj.uid[0]
        user = get_user_model().objects.filter(username=username).first()
        if user:
            # update attrs:
            user.email = lu_obj.mail[0]
            user.first_name = lu_obj.givenName[0]
            user.last_name = lu_obj.sn[0]
            user.origin = lc.__repr__()
            user.save()
        else:
            logger.info("--- Creating user: {}".format(username))
            user = get_user_model().objects.create(username=username,
                                                   email=lu_obj.mail[0],
                                                   first_name=lu_obj.givenName[0],
                                                   last_name=lu_obj.sn[0],
                                                   origin=lc.__repr__())

        # avoids another LDAP query in Attributes processors
        request.saml_session['identity_attributes'] = lu[dn]
        return user
