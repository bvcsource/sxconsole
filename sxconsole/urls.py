# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.conf.urls import include

from sxconsole.utils.urls import cbv_url_helper as url
from . import views


urlpatterns = [
    url(r'^$', views.HomeRelay),
    url(r'^stats/$', views.StatsView),
    url(r'^stats/get/$', views.GetStatsView),

    url(r'^tasks/$', views.TaskListView),
    url(r'^tasks/(?P<uuid>[\w\d-]+)/$', views.TaskStatusView),

    url(r'^api/', include('sxconsole.api.urls')),

    url(r'^admin/', include('sxconsole.accounts.urls')),
    url(r'^user/', include('sxconsole.users.root_urls')),
    url(r'^cluster/', include('sxconsole.clusters.urls')),
    url(r'^sx-management/', include('sxconsole.sx_management.urls')),

    url(r'^', include('django.conf.urls.i18n')),
    url(r'^tz/', include('tz_detect.urls')),
]
