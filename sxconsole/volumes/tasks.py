# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from sxconsole.celery import register_task
from sxconsole.models import TaskTypes
from sxconsole.sx_api import sx


def _delete_volume(self, vol_name):
    sx.deleteVolume(vol_name, force=True)

delete_volume = register_task(TaskTypes.DELETE_VOLUME)(_delete_volume)
