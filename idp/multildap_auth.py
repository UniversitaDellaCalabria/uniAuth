import logging

# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.sessions.models import Session
from django.conf import settings
from django.core.mail import send_mail
from django.db import connections
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from multildap.client import LdapClient
from . utils import get_encoded_username


logger = logging.getLogger(__name__)


class LdapUnicalMultiAcademiaAuthBackend(ModelBackend):
    """
        This class logout a user if another session of that user
        will be created

        in settings.py
        AUTHENTICATION_BACKENDS = [ 'idp.multildap_auth.LdapUnicalMultiAcademiaAuthBackend',
                                  ]
    """
    def authenticate(self, request, username=None, password=None):
        logger.info("--- LDAP BIND to MultiLKDAP proxy {} ---")

        user = None
        lu = None
        for lc in settings.LDAP_CONNECTIONS:
            lu = lc.get(search='(uid={})'.format(username))
            if lu:
                lu = type('', (object,), list(lu.values())[0])()
                break

        if not lu:
            logger.info("--- LDAP BIND failed for {} ---".format(username))
            return None

        # check if username exists and if it is active
        try:
            lc.authenticate(lu.uid,
                            password)
        except Exception as e:
            logger.info("--- LDAP {} seems to be unable to Auth ---".format(username))
            return None

        # persistent format as "urn:uuid:34087a09-8167-46d8-bade-aeae942fb65e"
        # uuid_username = uuid.uuid4().urn

        # username would be like an EPPN
        scoped_username = get_encoded_username(lu.uid)
        try:
            user = get_user_model().objects.get(username=scoped_username)
            # update attrs:
            if user.email != lu.mail[0]:
                user.email = lu.mail[0]
            if user.first_name != lu.cn:
                user.first_name = lu.cn
            if user.last_name != lu.sn:
                user.last_name = lu.sn
            user.save()
        except Exception as e:
            user = get_user_model().objects.create(username=scoped_username,
                                                   email=lu.mail[0],
                                                   first_name=lu.cn,
                                                   last_name=lu.sn)

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
