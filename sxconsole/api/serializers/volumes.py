# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import serializers

from sxconsole.entities import IndexingModes
from sxconsole.sx_api import sx
from sxconsole.utils.clusters import create_volume
from sxconsole.utils.volumes import update_volume
from sxconsole.volumes.validators import validate_volume_size, validate_name
from .common import SxObjectSerializer
from .fields import ChoicesField, SizeField


def get_new_volume_serializer():
    """Class definition wrapped in a function to dynamically enable/disable
    some fields."""

    class NewVolumeSerializer(SxObjectSerializer):
        name = serializers.CharField()
        size = SizeField()
        revisions = serializers.IntegerField()
        replicas = serializers.IntegerField()
        encryption = serializers.BooleanField(read_only=not sx.has_encryption)

        if sx.has_indexer:
            indexing = ChoicesField(choices=IndexingModes,
                                    default=IndexingModes.NO_INDEXING)
            indexing_display = serializers.CharField(
                source='get_indexing_display',
                read_only=True,
            )

        def create(self, data):
            create_volume(self.cluster, **data)
            return self.cluster.get_volume(data['name'], refresh=True)

        def validate_name(self, name):
            name = name.lower()
            valid, msg = validate_name(self.cluster, name)
            if valid:
                return name
            else:
                raise serializers.ValidationError(msg)

        def validate_size(self, size):
            current_size = self.instance.size if self.instance else 0
            valid, msg = validate_volume_size(self.cluster, size, current_size)
            if valid:
                return size
            else:
                raise serializers.ValidationError(msg)

        def validate_replicas(self, replicas):
            if self.cluster.replicas:
                return self.cluster.replicas
            return replicas

    return NewVolumeSerializer


def get_volume_serializer():
    """Class definition wrapped in a function to dynamically enable/disable
    some fields."""
    NewVolumeSerializer = get_new_volume_serializer()

    readonly_fields = ['encryption']
    if not sx.has_volume_replica_change:
        readonly_fields.append('replicas')
    if not sx.has_volume_rename:
        readonly_fields.append('name')

    class VolumeSerializer(NewVolumeSerializer):
        used_size = SizeField(read_only=True)

        def __init__(self, *args, **kwargs):
            for name in readonly_fields:
                self.fields[name].read_only = True
            super(VolumeSerializer, self).__init__(*args, **kwargs)

        def update(self, volume, data):
            update_volume(volume, data)
            volname = data.get('name', volume.name)
            return self.cluster.get_volume(volname, refresh=True)

        def validate_name(self, name):
            if name == self.instance.name:
                return name
            return super(VolumeSerializer, self).validate_name(name)

    return VolumeSerializer
