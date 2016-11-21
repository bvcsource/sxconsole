# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''


from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from sxconsole.accounts.models import Admin
from sxconsole.api.serializers.admins import AdminSerializer


class AdminViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet):
    base_name = 'admin'
    serializer_class = AdminSerializer

    def get_queryset(self):
        return Admin.objects.visible_to(self.request.user)

    def list(self, request, **kwargs):
        response = super(AdminViewSet, self).list(request, **kwargs)
        if not isinstance(response.data, dict):
            name = getattr(self, 'base_name_plural', self.base_name + 's')
            response.data = {name: response.data}
        return response
