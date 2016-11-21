# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from __future__ import absolute_import

import os

from django.utils.translation import ugettext_lazy as _

from .app import _check_permissions, SERVER_CONF, APP_CONF, EMAIL_CONF
from .common import BASE_DIR


def _path_from_config(key, default=None):
    """Return a path from config, with an optional default value.

    Relative paths are resolved in relation to `BASE_DIR`.
    """
    return os.path.join(BASE_DIR, SERVER_CONF.get(key, default))


# Core

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'sizefield',
    'rest_framework',
    'rest_framework_swagger',
    'tz_detect',

    'sxconsole',
    'sxconsole.clusters',
    'sxconsole.accounts',
    'sxconsole.volumes',
    'sxconsole.users',
    'sxconsole.api',

    'djcelery',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'sxconsole.middleware.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'tz_detect.middleware.TimezoneMiddleware',
    'sxconsole.middleware.ExtendSessionMiddleware',
    'sxconsole.middleware.ClusterConnectionMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': (os.path.join(BASE_DIR, 'templates'),),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sxconsole.context_processors.sx_console',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _path_from_config('db', 'db.sqlite3'),
    },
}
_check_permissions(DATABASES['default']['NAME'])


# Auth

LOGIN_URL = 'login'
AUTH_USER_MODEL = 'accounts.Admin'


# Server

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
WSGI_APPLICATION = 'sxconsole.wsgi.application'
ROOT_URLCONF = 'sxconsole.urls'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
    ('sxconsole', os.path.join(BASE_DIR, 'assets', 'build')),
    ('img', os.path.join(BASE_DIR, 'assets', 'img')),
)

SESSION_COOKIE_AGE = 60 * 60 * 24  # 1 day
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# Mailing

EMAIL_HOST = EMAIL_CONF.get('host')
EMAIL_PORT = EMAIL_CONF.get('port')
EMAIL_HOST_USER = EMAIL_CONF.get('user')
EMAIL_HOST_PASSWORD = EMAIL_CONF.get('password')
EMAIL_USE_SSL = EMAIL_CONF.get('ssl')
EMAIL_USE_TLS = EMAIL_CONF.get('tls')
DEFAULT_FROM_EMAIL = EMAIL_CONF.get('from')
SERVER_EMAIL = DEFAULT_FROM_EMAIL


# I18n

LANGUAGE_CODE = APP_CONF.get('default_lang', 'en')
LANGUAGES = (
    ('en', _("English")),
    ('de', _("German")),
    ('it', _("Italian")),
    ('pl', _("Polish")),
)
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'sx-translations', 'sxconsole'),
)
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# 3rd-party apps

REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS':
    'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_TASK_SOURCES = INSTALLED_APPS + (
    'sxconsole.sx_management.tasks',
    'sxconsole.clusters.access_log.fetch.prepare_access_log',
)
