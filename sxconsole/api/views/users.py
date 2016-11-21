# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from rest_framework import viewsets, mixins
from rest_framework.exceptions import NotFound

from sxconsole.api.permissions import UserPermission
from sxconsole.api.serializers.users import UserSerializer, NewUserSerializer
from sxconsole.utils.users import remove_user
from .common import SxObjectViewSetBase, DestroySxObjectMixin


class UserViewSet(SxObjectViewSetBase,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  DestroySxObjectMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (UserPermission,)
    base_name = 'user'

    def get_serializer_class(self):
        if self.action == 'create':
            return NewUserSerializer
        else:
            return UserSerializer

    def get_list(self):
        return self.cluster.users

    def get_object(self):
        try:
            email = self.kwargs['pk']
            user = self.cluster.get_user(email)
        except ValueError:
            raise NotFound()
        return user

    def perform_destroy(self, user):
        remove_user(user.email, self.cluster, self.cluster.is_root)
