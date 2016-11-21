# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.core.management.base import BaseCommand

from sxconsole.clusters.models import Cluster


class Command(BaseCommand):
    help = 'Removes expired tokens (e.g. password reset tokens)'

    def handle(self, *args, **kwargs):
        for cluster in Cluster.objects.filter(_expiration__isnull=False):
            expired = cluster.is_expired
            stored = bool(cluster.expiration.user_permissions)
            if expired and not stored:
                # This cluster is expired, but it didn't revoke permissions yet
                # (otherwise the user_permissions would not be empty)
                cluster.expiration.expire()
            elif stored and not expired:
                # This cluster is not yet expired, but there are some saved
                # permissions. Let's restore them
                cluster.expiration.restore(delete=False)
