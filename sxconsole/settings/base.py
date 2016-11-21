# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from .app import *  # noqa
from .app import DEMO
from .django import *  # noqa


if DEMO:
    DEMO_USER = 'demo@skylable.com'
    DEMO_PASS = 'demo'
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
