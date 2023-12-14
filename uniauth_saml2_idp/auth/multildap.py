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

        uid_value = 'uid'

        username = conv.escape_filter_chars(username, encoding=None)
        for lc in settings.LDAP_CONNECTIONS:
            # rewrites uid value if necessary
            uid_value = lc.conf.get('uid_alias', 'uid')
            search_filter = f"({uid_value}={username})"
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
            attrs = ",".join([i for i in list(lu.values())[0]])
            logger.info("--- LDAP user attributes: [{}]".format(attrs))

        username = getattr(lu_obj, uid_value)[0]
        user = get_user_model().objects.filter(username=username).first()
        mail = lu_obj.mail[0] if lu_obj.mail else ""
        sn = lu_obj.sn[0] if lu_obj.sn else ""
        gn = lu_obj.givenName[0] if lu_obj.givenName else ""

        if user:
            # update attrs:
            user.email = mail
            user.first_name = gn
            user.last_name = sn
            user.origin = lc.__repr__()
            user.save()
        else:
            logger.info("--- Creating user: {}".format(username))
            user = get_user_model().objects.create(
                username=username,
                email=mail,
                first_name=gn,
                last_name=sn,
                origin=lc.__repr__(),
            )

        # avoids another LDAP query in Attributes processors
        request.saml_session["identity_attributes"] = lu[dn]
        return user
