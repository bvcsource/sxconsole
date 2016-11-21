# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import serializers

from sxconsole.clusters.forms import update_cluster_expiration_date
from sxconsole.clusters.models import Cluster
from .fields import SizeField, ClusterExpirationField


class NewClusterSerializer(serializers.ModelSerializer):
    size = SizeField(help_text=Cluster._meta.get_field('size').help_text,
                     required=False, allow_null=True)
    expiration_date = ClusterExpirationField(required=False, allow_null=True)

    class Meta:
        model = Cluster
        fields = (
            'id', 'name', 'max_volumes', 'max_users', 'size',
            'thin_provisioning', 'replicas', 'expiration_date',
        )

    def save(self, **kwargs):
        instance = super(NewClusterSerializer, self).save(**kwargs)
        update_cluster_expiration_date(
            instance,
            self.validated_data.get('expiration_date'),
        )
        return instance

    def create(self, validated_data):
        validated_data.pop('expiration_date', None)
        instance = super(NewClusterSerializer, self).create(validated_data)
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('expiration_date', None)
        instance = super(NewClusterSerializer, self).update(
            instance,
            validated_data,
        )
        return instance


class ClusterSerializer(NewClusterSerializer):

    class Meta(NewClusterSerializer.Meta):
        read_only_fields = ('name',)
