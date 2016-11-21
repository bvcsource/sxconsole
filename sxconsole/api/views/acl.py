# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.utils.functional import cached_property
from rest_framework import viewsets, mixins
from rest_framework.exceptions import NotFound

from sxconsole.api.serializers.acl import VolumeAclSerializer
from .common import SxObjectViewSetBase


class VolumeAclViewSet(SxObjectViewSetBase,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = VolumeAclSerializer
    base_name = base_name_plural = 'acl'

    def get_serializer(self, *args, **kwargs):
        kwargs['volume'] = self.volume
        return super(VolumeAclViewSet, self).get_serializer(*args, **kwargs)

    @cached_property
    def volume(self):
        try:
            name = self.kwargs['volume_pk']
            volume = self.cluster.get_volume(name)
        except ValueError:
            raise NotFound()
        return volume

    def get_object(self):
        for acl in self.volume.acl:
            if acl['email'] == self.kwargs['pk']:
                return acl
        raise NotFound()

    def get_list(self):
        return self.volume.acl
