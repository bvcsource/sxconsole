# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.forms import ValidationError as DjangoValidationError
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from sxconsole import core
from sxconsole.core import size_validator
from sxconsole.users.validators import validate_email
from sxconsole.utils.users import add_user, invite_user, modify_user
from .common import SxObjectSerializer


class NewUserSerializer(SxObjectSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, validators=[core.password_validator], required=False,
        help_text=_("If omitted, a random password will be assigned."))
    quota = serializers.IntegerField(default=None)

    def create(self, data):
        email = data['email']
        new_user_created = add_user(self.cluster, **data)
        if new_user_created:
            invite_user(
                email=email,
                cluster=self.cluster,
            )
        return self.cluster.get_user(email, True)

    def validate_email(self, email):
        email = email.lower()
        valid, msg = validate_email(self.cluster, email)
        if valid:
            return email
        else:
            raise serializers.ValidationError(msg)

    def validate_quota(self, quota):
        if quota is None:
            return quota
        try:
            size_validator(quota)
            return quota
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)


class UserSerializer(SxObjectSerializer):
    email = serializers.EmailField(read_only=True)
    is_reserved = serializers.BooleanField(read_only=True)
    quota = serializers.IntegerField(default=None)
    quota_used = serializers.IntegerField(read_only=True)

    def update(self, user, data):
        modify_user(user, data)
        return self.cluster.get_user(user.email, refresh=True)
