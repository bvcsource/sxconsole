# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from .base import *  # noqa
from .django import REST_FRAMEWORK
from .logging import configure_logging


# Django

DEBUG = True
SECRET_KEY = 'jhy#v#c#_)i*h2bjcy5-%^kz0h=#c$r9wb_uie8vjj8n7qul@e'
SESSION_COOKIE_NAME = 'sessionid_devel'
LOGGING = configure_logging('.log/')


# 3rd party

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += \
    ('rest_framework.renderers.BrowsableAPIRenderer',)
