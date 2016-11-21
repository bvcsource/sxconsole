# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from logging import getLogger

from sxclient.exceptions import SXClientException

from sxconsole import core
from sxconsole.sx_api import sx


logger = getLogger(__name__)


def ensure_sxmonitor():
    sizes = (
        1024 ** 3 * 10,  # 10GB
        1024 ** 3,  # 1GB
        core._min_volume_size,
    )
    for size in sizes:
        try:
            replicas = len(sx.listNodes()['nodeList'])
        except SXClientException:
            replicas = core._min_replica_count

        try:
            if core.log_volname not in sx.listVolumes()['volumeList']:
                sx.createVolume(
                    core.log_volname,
                    volumeSize=size,
                    owner='admin',
                    replicaCount=replicas,
                    maxRevisions=1)
            return
        except SXClientException as e:
            if 'Invalid volume size' in e.message:
                continue

            logger.error('\n'.join((
                "SXClientException occurred while creating " +
                "sxmonitor volume!",
                "Exception: {}: {}".format(
                    type(e).__name__, e),
            )))
