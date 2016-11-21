# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import serializers

from sxconsole.sx_api import sx
from .common import SxObjectSerializer


class VolumeAclSerializer(SxObjectSerializer):
    email = serializers.EmailField(read_only=True)
    is_reserved = serializers.BooleanField(read_only=True)
    read = serializers.BooleanField()
    write = serializers.BooleanField()
    manager = serializers.BooleanField()

    def __init__(self, *args, **kwargs):
        # Fallback to None because Swagger doesn't provide context
        self.volume = kwargs.pop('volume', None)
        super(VolumeAclSerializer, self).__init__(*args, **kwargs)

    def update(self, acl, data):
        email = self.instance['email']
        perms = {
            '{action}-{perm}'.format(
                action='grant' if grant else 'revoke',
                perm=perm): [email]
            for perm, grant in data.items()}
        sx.updateVolumeACL(self.volume.full_name, perms)

        # Return updated acl
        self.instance.update(data)
        return self.instance
