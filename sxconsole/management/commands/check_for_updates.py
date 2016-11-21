# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from logging import getLogger

import requests
from django.core.management.base import BaseCommand

from sxconsole.core import version


logger = getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        version_msg = "Current SX Console version: {}".format(version)
        try:
            resp = requests.get(
                'http://cdn.skylable.com/check/sxconsole-version')
        except Exception as e:
            msg = version_msg + ".\nFailed to check for updates. Error: {}."
            logger.error(msg.format(e))
            return
        if resp.ok:
            msg = version_msg + ", latest version: {}"
            logger.info(msg.format(resp.text))
        else:
            msg = version_msg + ". Failed to check for updates ({}). "
            logger.warn(msg.format(resp.status_code))
