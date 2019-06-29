from django.conf import settings

def get_encoded_username(username):
    return '@'.join((username, settings.LDAP_BASE_DOMAIN))
