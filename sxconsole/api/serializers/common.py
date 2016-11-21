# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from sxclient.exceptions import SXClientException

from sxconsole import core


class SxObjectSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        # Fallback to None because Swagger doesn't provide context
        self.cluster = kwargs.pop('cluster', None)
        super(SxObjectSerializer, self).__init__(*args, **kwargs)

    def save(self, **kwargs):
        try:
            return super(SxObjectSerializer, self).save(**kwargs)
        except SXClientException as e:
            msg = core.get_exception_msg(e)
            raise ValidationError(msg)
