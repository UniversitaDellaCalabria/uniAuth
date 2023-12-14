"""
Django settings for django_idp project.

Generated by 'django-admin startproject' using Django 2.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import ldap
import os
import logging
import sys

from .settingslocal import *

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# use settingslocal
# DEBUG = True
# SESSION_EXPIRE_AT_BROWSER_CLOSE=True
# SESSION_COOKIE_AGE = 60 * 10 # minutes
# SECRET_KEY = settingslocal.SECRET_KEY
# ALLOWED_HOSTS = settingslocal.ALLOWED_HOSTS

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # CSRF_USE_SESSIONS = True

# Application definition

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # SameSite Cookie workaround
    "djangosaml2.middleware.SamlSessionMiddleware",
]

# GETTEXT LOCALIZATION
MIDDLEWARE.append("django.middleware.locale.LocaleMiddleware")
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)
#

ROOT_URLCONF = "django_idp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "sass_processor.finders.CssFinder",
]

WSGI_APPLICATION = "django_idp.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    # TODO
    # 'unical_ict.auth.SessionUniqueBackend',
]

#################
# LDAP, optional
#################
if "ldap_peoples" in INSTALLED_APPS:
    # load default and overrides as you prefer
    from ldap_peoples.settings import *

    DEFAULT_EDUPERSON_ENTITLEMENT = [
        "urn:mace:terena.org:tcs:personal-user",
        "urn:mace:terena.org:tcs:escience-user",
    ]
    SCHAC_HOMEORGANIZATIONTYPE_DEFAULT = ["educationInstitution", "university"]
    SCHAC_HOMEORGANIZATION_DEFAULT = LDAP_BASE_DOMAIN

    LDAP_CONNECTION_OPTIONS = {
        ldap.OPT_PROTOCOL_VERSION: 3,
        ldap.OPT_NETWORK_TIMEOUT: 5,
        # ldap.OPT_DEBUG_LEVEL: 255,
        # ldap.OPT_X_TLS_CACERTFILE: LDAP_CACERT,
        # force /etc/ldap.conf configuration.
        # ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER,
        # ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_DEMAND,
        # ldap.OPT_X_TLS: ldap.OPT_X_TLS_DEMAND,
        # ldap.OPT_X_TLS_DEMAND: True,
        # ldap.OPT_X_TLS: ldap.OPT_X_TLS_NEVER,
        # ldap.OPT_X_TLS_DEMAND: False,
    }

    DATABASES["ldap"] = {
        "ENGINE": "ldapdb.backends.ldap",
        # only in localhost
        # 'NAME': 'ldapi://',
        "NAME": LDAP_DB_URL,
        "USER": LDAP_CONNECTION_USER,
        "PASSWORD": LDAP_CONNECTION_PASSWD,
        "RETRY_DELAY": 8,
        "RETRY_MAX": 3,
        "CONNECTION_OPTIONS": LDAP_CONNECTION_OPTIONS,
    }

    DATABASE_ROUTERS = ["ldapdb.router.Router"]
    AUTHENTICATION_BACKENDS.append(
        "uniauth_saml2_idp.auth.ldap_peoples.LdapAcademiaAuthBackend"
    )

if "multildap" in INSTALLED_APPS:
    AUTHENTICATION_BACKENDS.append(
        "uniauth_saml2_idp.auth.multildap.LdapUnicalMultiAcademiaAuthBackend"
    )


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "data/media")

if "uniauth_saml2_idp" in INSTALLED_APPS:
    pass
