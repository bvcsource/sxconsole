# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import viewsets
from rest_framework.exceptions import NotFound

from sxconsole.api.permissions import VolumePermission
from sxconsole.api.serializers.volumes import (
    get_volume_serializer, get_new_volume_serializer,
)
from sxconsole.sx_api import sx
from .common import SxObjectViewSet


class VolumeViewSet(SxObjectViewSet, viewsets.ModelViewSet):
    permission_classes = (VolumePermission,)
    base_name = 'volume'

    def get_serializer_class(self):
        if self.action == 'create':
            return get_new_volume_serializer()
        else:
            return get_volume_serializer()

    def get_list(self):
        return self.cluster.volumes

    def get_object(self):
        try:
            name = self.kwargs['pk']
            volume = self.cluster.get_volume(name)
        except ValueError:
            raise NotFound()
        return volume

    def perform_destroy(self, volume):
        sx.deleteVolume(volume.full_name, force=True)
