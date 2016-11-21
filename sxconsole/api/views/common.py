# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.utils.functional import cached_property
from rest_framework import viewsets, mixins
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from sxclient.exceptions import SXClientException

from sxconsole import core
from sxconsole.clusters.models import Cluster


class SxObjectViewSetBase(object):
    lookup_value_regex = r'[^/]+'

    @cached_property
    def cluster(self):
        """Try to obtain a Cluster instance or raise 404."""
        try:
            return self.request.user.clusters.get(pk=self.kwargs['cluster_pk'])
        except (Cluster.DoesNotExist, ValueError):
            raise NotFound()

    def get_serializer(self, *args, **kwargs):
        kwargs['cluster'] = self.cluster
        return super(SxObjectViewSetBase, self).get_serializer(*args, **kwargs)

    def list(self, request, **kwargs):
        objects = self.get_list()
        serializer = self.get_serializer(objects, many=True)
        name = getattr(self, 'base_name_plural', self.base_name + 's')
        return Response({name: serializer.data})


class DestroySxObjectMixin(mixins.DestroyModelMixin):

    def destroy(self, request, *args, **kwargs):
        try:
            return super(DestroySxObjectMixin, self) \
                .destroy(request, *args, **kwargs)
        except SXClientException as e:
            msg = core.get_exception_msg(e)
            return Response(msg, status=400)


class SxObjectViewSet(SxObjectViewSetBase, DestroySxObjectMixin,
                      viewsets.ModelViewSet):
    """Base viewset for handling vcluster objects like volumes and users."""

    def get_queryset(self):
        return  # Silence the DRF exception
