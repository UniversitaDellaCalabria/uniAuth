# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lrx(fg&+2e=$l=y8$!+l68_=-lm3*n+myg%r3z!yjm(lg*l%-z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_COOKIE_AGE = 60 * 10 # minutes

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'accounts',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sass_processor',
    'bootstrap_italia_template',
    'django_unical_bootstrap_italia',
    'uniauth',
    'uniauth_unical_template',
    # 'ldap_peoples',
    # 'multildap',
    'rangefilter']

AUTH_USER_MODEL = "accounts.User"

# ldap_peoples related
# LDAP_CONNECTION_USER = 'cn=thatuser,dc=unical,dc=it'
# LDAP_CONNECTION_PASSWD = 'Thatpassword'
# LDAP_DB_URL = 'ldap://localhost:389/'
#LDAP_BASE_DOMAIN = 'unical.it'
# LDAP_PEOPLE_DN = 'dc=proxy'

# needed for ldap admin forms
DATETIME_INPUT_FORMATS = ['%Y-%m-%d %H:%M:%S',
                          '%d/%m/%Y %H:%M:%S']

DATE_INPUT_FORMATS = ['%Y-%m-%d', '%d/%m/%Y']

ADMINS = [('name surname', 'user1@DOMAIN'),
          ('name surnale', 'user2@DOMAIN'),]

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'detailed': {
            'format': '[%(asctime)s] %(message)s [(%(levelname)s)]' # %(name)s.%(funcName)s:%(lineno)s]'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'formatter': 'detailed',
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'formatter': 'detailed',
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'uniauth': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
