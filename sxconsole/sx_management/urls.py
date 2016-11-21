# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.conf import settings

from sxconsole.utils.urls import cbv_url_helper as url
from . import views


def get_urlpatterns():
    if settings.APP_CONF.get('disable_sx_management'):
        return []
    else:
        return [
            url(r'^$', views.ClusterManagementView),
            url(r'^mark-nodes-as-faulty/$', views.MarkNodesAsFaultyView),
            url(r'^replace-faulty-nodes/$', views.ReplaceFaultyNodesView),
            url(
                r'^modify-cluster-configuration/$',
                views.ModifyClusterConfigurationView),
        ]

urlpatterns = get_urlpatterns()
