from django.conf import settings

def get_encoded_username(username):
    if isinstance(username, list):
        username = username[0]
    return '@'.join((username, settings.LDAP_BASE_DOMAIN))
