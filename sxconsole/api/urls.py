# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.conf.urls import url, include
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_nested import routers

from . import views


latest_version_redirect = RedirectView.as_view(
    permanent=False, url=reverse_lazy('v1:api-root'))

router = routers.DefaultRouter()
router.register(r'admins', views.AdminViewSet, base_name='admin')
router.register(r'clusters', views.ClusterViewSet, base_name='cluster')

clusters_router = routers.NestedSimpleRouter(
    router, r'clusters', lookup='cluster')

clusters_router.register(
    r'admins',
    views.ClusterAdminViewSet,
    base_name='admins',
)
clusters_router.register(r'volumes', views.VolumeViewSet, base_name='volume')
volumes_router = routers.NestedSimpleRouter(
    clusters_router, r'volumes', lookup='volume')
volumes_router.register(r'acl', views.VolumeAclViewSet, base_name='acl')

clusters_router.register(r'users', views.UserViewSet, base_name='user')

v1_urls = [
    url(r'^', include(router.urls)),
    url(r'^', include(clusters_router.urls)),
    url(r'^', include(volumes_router.urls)),
    url(r'^tasks/(?P<uuid>[\w\d-]+)/', views.task_status),
]

urlpatterns = [
    url(r'^$', latest_version_redirect),
    url(r'^v1/', include(v1_urls, namespace='v1')),
    url(r'^auth/', obtain_jwt_token),
    url(r'^docs/', include('sxconsole.api.swagger_urls')),
]
