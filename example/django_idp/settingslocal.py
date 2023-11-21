import json
import os

from . idp_pysaml2 import HOST, ENTITY_URL
from . settingslocal_logging import LOGGING

MFA_DOMAIN = ENTITY_URL
MFA_SITE_TITLE = os.getenv("MFA_SITE_TITLE", "uniAuth-IDP-example")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", 'lrx(fg&+2e="$TDdssdG$%TSFFDSFfdfsmyg%r3z!yjm(lg*l%-z')

# CORS are needed for OAS3 app
CORS_ORIGIN_ALLOW_ALL = bool(int(os.environ.get("CORS_ORIGIN_ALLOW_ALL", 0)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", 1))
if not DEBUG:
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SESSION_COOKIE_AGE = os.environ.get(
        "SESSION_COOKIE_AGE",
        60 * 15 # 10 minutes
    )
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# the path corresponding the admin backend, default if not defined: admin/
ADMIN_PATH = os.environ.get("ADMIN_PATH", 'admin_access')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', [HOST, "localhost", "127.0.0.1", "*"])
AUTH_USER_MODEL = 'accounts.User'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

INSTALLED_APPS = [
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sass_processor',

    # templates
    'custom_template',
    #  'django_unical_bootstrap_italia',
    'bootstrap_italia_template',

    # uniauth idp
    'uniauth_saml2_idp',
    # 'ldap_peoples',
    
    # file upload/change/delete cleanup
    'django_cleanup.apps.CleanupConfig',
    
    # 'multildap',
    # 'rangefilter'

    "corsheaders",
    
    # proxy
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.azure",
    "allauth.socialaccount.providers.microsoft",
    
    # custom
    "socialauth",
    
    # password reset
    "django_form_builder",
    "password_reset",
    
    # mfa
    "mfa"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    
    # GETTEXT
    "django.middleware.locale.LocaleMiddleware",
    
    # SameSite Cookie workaround
    "djangosaml2.middleware.SamlSessionMiddleware",
]

if os.environ.get("MFA", 0):
    # Enforce MFA
    MIDDLEWARE.append("mfa.middleware.MFAEnforceMiddleware"
)

if "allauth" in INSTALLED_APPS:
    MIDDLEWARE.append("allauth.account.middleware.AccountMiddleware")

if 'multildap' in INSTALLED_APPS:
    from . settingslocal_ldap import *

if 'multildap' in INSTALLED_APPS or 'ldap_peoples' in INSTALLED_APPS:
    # ldap_peoples related
    # LDAP_CONNECTION_USER = 'cn=thatuser,dc=unical,dc=it'
    # LDAP_CONNECTION_PASSWD = 'Thatpassword'
    # LDAP_DB_URL = 'ldap://localhost:389/'
    LDAP_BASE_DOMAIN = 'local'
    # LDAP_PEOPLE_DN = 'dc=proxy'

if os.getenv("DATABASES", None):
    DATABASES = json.loads(os.getenv("DATABASES"))
else:
    DATABASES = {
        # 'default': {
            # 'ENGINE': 'django.db.backends.mysql',
            # 'NAME': 'uniauth',
            # 'HOST': 'localhost',
            # 'USER': 'that-user',
            # 'PASSWORD': 'that-password',
            # 'PORT': '',
            # 'OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
        # },
        #  'default': {
            #  'ENGINE': 'django.db.backends.postgresql',
            #  'NAME': os.environ.get("DB-NAME", 'uniauth'),
            #  'USER': os.environ.get("DB-USER", 'uniauth'),
            #  'PASSWORD': os.environ.get("DB-PASS", 'that-pass'),
            #  'HOST': os.environ.get("DB-HOST", 'uniauth-db'),
            #  'PORT': os.environ.get("DB-PORT", '5432'),
            #  'OPTIONS': {
                #  'options': os.getenv("POSTGRESQL_OPTION_CLI", '-c statement_timeout=5000'),
                #  'connect_timeout': os.getenv("POSTGRESQL_CONNECT_TIMEOUT", 5)
            #  }
        #  }
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
       }
    }

# needed for ldap admin forms
DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',
    '%d/%m/%Y %H:%M:%S'
]

DATE_INPUT_FORMATS = ['%Y-%m-%d', '%d/%m/%Y']

# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# email notification on error 500
DEFAULT_FROM_EMAIL = 'idp-noreply@DOMAIN'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_HOST = 'smtp.example.org'
# EMAIL_HOST_USER = 'myemail@hotmail.com'
# EMAIL_HOST_PASSWORD = 'mypassword'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMINS = [('name surname', 'user1@DOMAIN'),
          ('name surnale', 'user2@DOMAIN'),]


# Provider specific settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
            'openid',
            # 'https://www.googleapis.com/auth/calendar.readonly'
        ],
    },
    #  'microsoft': {"SCOPE": ["https://outlook.office365.com/.default", "email", "openid"]}
    # 'azure' :{}
}

# Mail is sent using the SMTP host and port specified in the 
# EMAIL_HOST and EMAIL_PORT settings. The EMAIL_HOST_USER and EMAIL_HOST_PASSWORD 
# settings, if set, are used to authenticate to the SMTP server, and the 
# EMAIL_USE_TLS and EMAIL_USE_SSL settings control whether a secure connection is used.

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv(
    "EMAIL_BACKEND",
    None
)
EMAIL_PORT = os.getenv(
    "EMAIL_PORT",
    None
)
EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    None
)
EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    None
)
EMAIL_USE_TLS = os.getenv(
    "EMAIL_USE_TLS",
    None
)
EMAIL_USE_SSL = os.getenv(
    "EMAIL_USE_SSL",
    None
)
EMAIL_FROM = os.getenv(
    "EMAIL_FROM",
    "no-reply@xdrplus-iam.acsia.org"
)
EMAIL_SUBJECT_PASSWD_RESET = os.getenv(
    "EMAIL_SUBJECT_PASSWD_RESET",
    "A password reset was requested"
)
EMAIL_MSG_PASSWD_RESET = os.getenv(
    "EMAIL_MSG_PASSWD_RESET",
    """
    Dear {user},
    
    You have requested a password change for {host}.
    Please click on the link below to confirm the password 
    that you have provided previously during your request:
    
    {link}
    
    best regards 
    """
)

LOGIN_REDIRECT_URL = "/idp/login/process/"

# DISABLE USER SIGNUP
ACCOUNT_ADAPTER = 'socialauth.account_adapter.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'socialauth.socialaccount_adapter.CustomSocialAccountAdapter'


# account linking based on email
# ACCOUNT_AUTHENTICATION_METHOD = "username_email"
# ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# This option can be used to set whether an email verification is necessary for a user to log in after he registers an account.
# ACCOUNT_EMAIL_REQUIRED = True

# ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_AUTHENTICATION_METHOD = 'email'

# SOCIALACCOUNT_EMAIL_REQUIRED = True
# SOCIALACCOUNT_AUTO_SIGNUP = False

# TODO REMOVE
# EMAIL_VERIFICATION = None
# SOCIALACCOUNT_EMAIL_VERIFICATION = None
