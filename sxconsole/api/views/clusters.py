# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.utils.functional import cached_property
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sxconsole.api.permissions import ClusterPermission
from sxconsole.api.serializers.clusters import (
    ClusterSerializer, NewClusterSerializer,
)
from sxconsole.clusters.models import Cluster


class ClusterViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, ClusterPermission,)
    base_name = 'cluster'

    def get_serializer_class(self):
        if self.action == 'create':
            return NewClusterSerializer
        else:
            return ClusterSerializer

    def get_queryset(self):
        return self.request.user.clusters.all()

    def list(self, request, **kwargs):
        response = super(ClusterViewSet, self).list(request, **kwargs)
        if not isinstance(response.data, dict):
            name = getattr(self, 'base_name_plural', self.base_name + 's')
            response.data = {name: response.data}
        return response


class ClusterAdminViewSet(viewsets.GenericViewSet):
    base_name = 'cluster-admin'
    permission_classes = (IsAuthenticated,)

    @cached_property
    def cluster(self):
        """Try to obtain a Cluster instance or raise 404."""
        try:
            return self.request.user.clusters.get(pk=self.kwargs['cluster_pk'])
        except (Cluster.DoesNotExist, ValueError):
            raise NotFound()

    def list(self, request, *args, **kwargs):
        name = getattr(self, 'base_name_plural', self.base_name + 's')
        data = self.cluster.admins.values_list('pk', flat=True)
        return Response({name: data})

    def update(self, request, *args, **kwargs):
        try:
            admin_pk = self.kwargs['pk']
            self.cluster.admins.add(admin_pk)
        except (KeyError, ValueError):
            raise ParseError()
        else:
            return Response(status=204)

    def destroy(self, *args, **kwargs):
        try:
            admin_pk = self.kwargs['pk']
            self.cluster.admins.remove(admin_pk)
        except (KeyError, ValueError):
            raise ParseError()
        else:
            return Response(status=204)
