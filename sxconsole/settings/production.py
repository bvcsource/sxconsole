# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from __future__ import absolute_import

import os

from django.utils.crypto import get_random_string

from .app import APP_CONF, SERVER_CONF, _check_permissions
from .base import *  # noqa
from .django import SERVER_EMAIL
from .logging import configure_logging


_secret_key_path = '/data/django_secret_key'

if not os.path.exists(_secret_key_path):
    with open(_secret_key_path, 'w') as f:
        f.write(get_random_string(50))

    os.chmod(_secret_key_path, 0400)


def _as_list(value):
    """Ensure that the value is a list."""
    if not isinstance(value, list):
        value = [value]
    return value


# Django

_check_permissions(_secret_key_path)
with open(_secret_key_path) as f:
    SECRET_KEY = f.read()

DEBUG = False
ALLOWED_HOSTS = _as_list(SERVER_CONF['hosts'])
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
LOGGING = configure_logging('/srv/logs/')

ADMINS = APP_CONF.get('report_to')
if ADMINS:
    assert SERVER_EMAIL, \
        "The `mailing.from` field is required if `app.report_to` is given."
    ADMINS = [('Admin', email) for email in _as_list(ADMINS)]
