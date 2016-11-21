# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

import os

import yaml

from .common import BASE_DIR


def _check_permissions(path):
    if not os.path.isfile(path):
        return
    permissions = os.stat(path).st_mode
    assert oct(permissions)[-2:] == '00', (
        "Please make sure that this file is not "
        "accessible to other users: {}".format(path))


# Load sxconsole config

_conf_path = os.path.join(BASE_DIR, 'conf.yaml')
_check_permissions(_conf_path)
with open(_conf_path) as f:
    ROOT_CONF = yaml.safe_load(f)
    SERVER_CONF = ROOT_CONF.get('server') or {}
    APP_CONF = ROOT_CONF.get('app') or {}
    SX_CONF = ROOT_CONF.get('sx') or {}
    EMAIL_CONF = ROOT_CONF.get('mailing') or {}
    CARBON_CONF = ROOT_CONF.get('carbon') or {}
    CELERY_CONF = ROOT_CONF.get('celery') or {}
    STATS_CONF = APP_CONF.get('stats') or {}


# Whitelabel

_skin_name = ROOT_CONF.get('skin', 'default')
_skin_path = os.path.join(BASE_DIR, 'skins', _skin_name, 'skin.yaml')
with open(_skin_path) as f:
    SKIN = yaml.safe_load(f)


# App-specific settings

APP_URL = SERVER_CONF['sxconsole_url']
DEMO = SERVER_CONF.get('demo', False)
S3IMPORT_THREAD_NUMBER = CELERY_CONF.get('s3import_thread_num') or 1
