# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.conf.urls import include

from sxconsole.utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [

    url(r'^add/$', views.CreateClusterView),
    url(r'^search/$', views.SearchClustersView),
    url(r'^(?P<pk>\d+)/$', views.DisplayClusterView),
    url(r'^(?P<pk>\d+)/edit/$', views.UpdateClusterView),
    url(r'^(?P<pk>\d+)/delete/$', views.DeleteClusterView),
    url(r'^(?P<pk>\d+)/add_admin/$', views.AddClusterAdminView),
    url(r'^(?P<pk>\d+)/remove_admin/(?P<admin_pk>\d+)/$',
        views.RemoveClusterAdminView),
    url(r'^(?P<pk>\d+)/logs/$', views.AccessLogsFormView),
    url(r'^(?P<pk>\d+)/logs/(?P<task_id>[-\w]+)/$',
        views.AccessLogsResultsView),
    url(r'^(?P<pk>\d+)/s3import/$', views.S3ImportView),
    url(r'^(?P<pk>\d+)/s3import/(?P<taskid>[-\da-f]+)/$',
        views.S3ImportSingleTaskView),

    url(r'^(?P<pk>\d+)/volume/', include('sxconsole.volumes.urls')),
    url(r'^(?P<pk>\d+)/user/', include('sxconsole.users.urls')),
]
