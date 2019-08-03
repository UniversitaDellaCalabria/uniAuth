import ldap
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.sessions.models import Session
# from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.db import connections
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ldap_peoples.models import LdapAcademiaUser
from . utils import get_encoded_username


logger = logging.getLogger(__name__)


class LdapAcademiaAuthBackend(ModelBackend):
    """
        This class logout a user if another session of that user
        will be created

        in settings.py
        AUTHENTICATION_BACKENDS = [ 'idp.ldap_auth.backends.ModelBackend',
                                    'ldap_peoples.auth.LdapAcademiaAuthBackend'
                                  ]
    """
    def authenticate(self, request, username=None, password=None):
        ldap_conn = connections['ldap']
        user = None
        lu = LdapAcademiaUser.objects.filter(uid=username).first()
        if not lu:
            logger.info("--- LDAP BIND failed for {} ---".format(username))
            return None

        # check if username exists and if it is active
        try:
            ldap_conn.connect()
            ldap_conn.connection.bind_s(lu.distinguished_name(),
                                        password)
            ldap_conn.connection.unbind_s()
        except Exception as e:
            logger.info("--- LDAP {} seems to be unable to Auth ---".format(username))
            return None

        # if account beign unlocked this will be always false
        if not lu.is_active():
            logger.info("--- LDAP {} seems to be disabled ---".format(username))
            return None

        # username would be like an EPPN
        scoped_username = get_encoded_username(lu.uid)
        try:
            user = get_user_model().objects.get(username=scoped_username)
            # update attrs:
            user.email = lu.mail[0]
            user.first_name = lu.cn
            user.last_name = lu.sn
            user.origin = 'ldap_peoples'
            user.original_uid = username
            user.save()
        except Exception as e:
            user = get_user_model().objects.create(username=scoped_username,
                                                   email=lu.mail[0],
                                                   first_name=lu.cn,
                                                   last_name=lu.sn,
                                                   origin = 'ldap_peoples',
                                                   original_uid = username)

        # TODO: Create a middleware for this
        # disconnect already created session, only a session per user is allowed
        # get all the active sessions
        # if not settings.MULTIPLE_USER_AUTH_SESSIONS:
            # for session in Session.objects.all():
                # try:
                    # if int(session.get_decoded()['_auth_user_id']) == user.pk:
                        # session.delete()
                # except (KeyError, TypeError, ValueError):
                    # pass

        return user
