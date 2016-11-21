# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import serializers

from sxconsole.models import TaskMeta
from .fields import ChoicesField


class TaskMetaSerializer(serializers.ModelSerializer):

    type = ChoicesField(choices=TaskMeta.TYPES)
    type_display = serializers.CharField(
        source='get_type_display',
        read_only=True,
    )
    info = serializers.SerializerMethodField()

    def get_info(self, obj):
        info = obj.info
        if isinstance(info, Exception):
            return str(info)
        return info

    class Meta:
        model = TaskMeta
        fields = (
            'id', 'type', 'type_display', 'cluster', 'admin', 'queue_date',
            'start_date', 'end_date', 'ready', 'status', 'info')
