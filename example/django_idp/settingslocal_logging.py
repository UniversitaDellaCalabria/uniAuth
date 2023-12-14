import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'idp_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': f'{BASE_DIR}/logs/uniauth.log',
            'maxBytes': 1024 * 100,
            'backupCount': 33,
        },
        'django_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': f'{BASE_DIR}/logs/django.log',
            'maxBytes': 1024 * 100,
            'backupCount': 33,
        },
    },
    'loggers': {
        # disables Invalid HTTP_HOST header emails
        'django.security.DisallowedHost': {
                'handlers': ['mail_admins'],
                'level': 'CRITICAL',
                'propagate': False,
        },
        'django': {
            'handlers': ['django_file', 'console', 'mail_admins'],
            'level': 'INFO',
            'propagate': True,
        },
        'uniauth_saml2_idp': {
            'handlers': ['idp_file', 'console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'multildap': {
            'handlers': ['idp_file', 'console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'pysaml2': {
            'handlers': ['idp_file', 'console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'password_reset': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
