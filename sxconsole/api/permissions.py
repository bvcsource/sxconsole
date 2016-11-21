# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from sxconsole.utils.clusters import can_add_user
from sxconsole.volumes.validators import can_add_volume


class ClusterPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_superadmin

    def has_object_permission(self, request, view, cluster):
        has_cluster = request.user.clusters.filter(pk=cluster.pk).exists()
        is_safe = request.method in permissions.SAFE_METHODS
        if not has_cluster:
            return False
        elif is_safe:
            return True
        elif cluster.is_root:
            return is_safe
        else:
            return request.user.is_superadmin


class SxObjectPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False

        view.cluster  # Raises 404 if cluster is missing

        if view.action == 'create':
            can, msg = self.can_add(view.cluster, request.user)
            if not can:
                raise PermissionDenied(msg)
        return True


class VolumePermission(SxObjectPermission):
    can_add = staticmethod(can_add_volume)


class UserPermission(SxObjectPermission):
    can_add = staticmethod(can_add_user)
