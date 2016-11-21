# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import serializers

from sxconsole.accounts.models import Admin, AdminLevels
from .fields import ChoicesField


class AdminSerializer(serializers.ModelSerializer):

    level = ChoicesField(choices=AdminLevels)
    level_display = serializers.CharField(source='get_level_display',
                                          read_only=True)

    class Meta:
        model = Admin
        fields = ('id', 'level', 'level_display', 'email')
