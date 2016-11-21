# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.utils.translation import ugettext_lazy as _

from sxconsole import core
from sxconsole.sx_api import sx
from sxconsole.utils.sx import get_configuration_nodes


def get_free_size(cluster, volume=None):
    cluster_free_space = get_free_cluster_space(volume=volume)
    if not cluster.size or cluster.thin_provisioning:
        return cluster_free_space

    # Does the vcluster have even less space?
    used_space = sum(v.size for v in cluster.volumes)
    if volume:
        used_space -= volume.size

    vcluster_free_space = max(cluster.size - used_space, 0)
    return min(cluster_free_space, vcluster_free_space)


def get_allocated_space(cluster):
    return sum(v.size for v in cluster.volumes)


def get_free_cluster_space(volume=None):
    """Calculate free space from the space allocated by volumes."""
    nodes = get_configuration_nodes()
    used_space = sum(v['sizeBytes'] * v['replicaCount']
                     for v in sx.listVolumes()['volumeList'].values())
    if volume:
        used_space -= volume.size * volume.replicas
    cluster_free_space = sum(n['nodeCapacity'] for n in nodes) - used_space
    return cluster_free_space


def can_add_user(cluster, user):
    """For given user and cluster, checks if the user can add a sx user.

    Returns a tuple of (can, msg). If can is True, msg is None.
    """
    if cluster.max_users and len(cluster.users) >= cluster.max_users:
        return False, _(
            "You can't add a new user because you have reached "
            "the max users limit.")
    elif cluster.is_expired and not user.is_superadmin:
        return False, _(
            "You can't add a new user because this cluster has expired.")
    else:
        return True, None


def create_volume(cluster, name, size, replicas, revisions, encryption=None,
                  indexing=None):
    """
    For given cluster and volume parameters, creates a volume inside the
    vcluster.
    """
    volume_name = cluster.build_name(name)
    owner = cluster.build_volume_owner()

    def build_volume_meta():
        meta = cluster.build_volume_meta()
        if encryption:
            meta.update(core.generate_encryption_meta())
        return meta

    meta = build_volume_meta()

    sx.createVolume(
        volume=volume_name, volumeSize=size, owner=owner,
        replicaCount=replicas, maxRevisions=revisions,
        volumeMeta=meta)

    # Set volume indexing
    if indexing:
        cluster.get_volume(name, refresh=True).set_indexing(indexing)
