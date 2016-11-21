# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from sxconsole.utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [
    url(r'^add/$', views.CreateVolumeView),
    url(r'^(?P<name>[^/]+)/acl$', views.VolumeAclView),
    url(r'^(?P<name>[^/]+)/edit/$', views.UpdateVolumeView),
    url(r'^(?P<name>[^/]+)/delete/$', views.DeleteVolumeView),
    url(r'^(?P<name>[^/]+)/make_public/$', views.MakeVolumePublic),
    url(r'^(?P<name>[^/]+)/make_private/$', views.MakeVolumePrivate),
]
