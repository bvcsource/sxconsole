# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.conf.urls import url
from django.http import Http404

from rest_framework_swagger.views import \
    SwaggerResourcesView, SwaggerApiView, SwaggerUIView


class AccessControl(object):
    """Mixin for custom access control in swagger views."""

    def initial(self, request, *args, **kwargs):
        if self.request.user.is_authenticated() and \
                self.request.user.is_superadmin:
            return super(AccessControl, self) \
                .initial(request, *args, **kwargs)
        raise Http404()

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated() and \
                self.request.user.is_superadmin:
            return super(AccessControl, self) \
                .dispatch(request, *args, **kwargs)
        raise Http404()


ui = type('SwaggerUIView', (AccessControl, SwaggerUIView), {}).as_view()
resources = type('SwaggerResourcesView', (AccessControl, SwaggerResourcesView),
                 {}).as_view()
api = type('SwaggerApiView', (AccessControl, SwaggerApiView), {}).as_view()

urlpatterns = [
    url(r'^$', ui, name="django.swagger.base.view"),
    url(r'^api-docs/$', resources, name="django.swagger.resources.view"),
    url(r'^api-docs/(?P<path>.*)/?$', api, name='django.swagger.api.view'),
]
