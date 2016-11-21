# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.utils.translation import ugettext_lazy as _

from sxconsole.utils import clusters


def can_add_volume(cluster, user):
    """For given user and cluster, checks if the user can add a volume.

    Returns a tuple of (can, msg). If can is True, msg is None.
    """
    if cluster.max_volumes and len(cluster.volumes) >= cluster.max_volumes:
        return False, _(
            "You can't add a new volume because you have reached "
            "the max volumes limit.")
    elif cluster.is_expired and not user.is_superadmin:
        return False, _(
            "You can't add a new volume because this cluster has expired.")
    else:
        return True, None


def validate_volume_size(cluster, size, current_size):
    """
    Called when creating/updating a volume, to check its new size against
    cluster limits.
    """
    if (
            cluster.thin_provisioning or
            not cluster.size or
            (current_size != 0 and size < current_size)
    ):
        return True, None
    max_size = clusters.get_free_size(cluster) - current_size
    if size > max_size:
        return False, _(
            "You are running out of space on this cluster. "
            "Enter a smaller size and try again.")
    return True, None


def validate_name(cluster, name):
    name = name.lower()
    for volume in cluster.volumes:
        if name == volume.name.lower():
            return False, _("This volume already exists.")
    return True, None
