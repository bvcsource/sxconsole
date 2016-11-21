# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import json
from collections import OrderedDict

from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from django.http import Http404, JsonResponse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from sxconsole.clusters.models import Cluster
from sxconsole.entities import Node
from sxconsole.models import TaskMeta
from sxconsole.stats import StatsFetcher
from sxconsole.sx_api import sx
from sxconsole.utils.decorators import super_admin_only


class HomeRelay(generic.TemplateView):
    """Chooses the home page for the user."""
    url_name = 'home'

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_superadmin:
            cbv = SuperAdminHomeView
        else:
            cbv = AdminHomeView
        return cbv.as_view()(*args, **kwargs)


class AdminHomeView(generic.TemplateView):
    template_name = 'admin_home.html'
    title = _("Dashboard")

    def get_context_data(self, **kwargs):
        """Show data of the user's clusters."""
        clusters = self.request.user.clusters.all()
        total_clusters = len(clusters)
        clusters_size = sum(c.size for c in clusters if c.size)
        used_size = sum(c.used_size for c in clusters)

        return super(AdminHomeView, self).get_context_data(
            total_clusters=total_clusters, clusters_size=clusters_size,
            used_size=used_size, **kwargs)


@super_admin_only
class SuperAdminHomeView(generic.TemplateView):
    template_name = 'superadmin_home.html'
    title = _("Dashboard")

    @cached_property
    def nodes(self):
        return Node.get_current_nodes()

    def get_cluster_context(self):
        """Show info about the physical cluster."""
        nodes_down = any(n.down for n in self.nodes)

        physical_size = None if nodes_down else \
            sum(n.used_space + n.free_space for n in self.nodes)
        cluster = {
            'address': 'sx://{}'.format(sx._cluster.name or
                                        sx._cluster.host),
            'port': sx._cluster.port or (
                443 if sx._cluster.is_secure else 80),
            'virtual_size': sum(n.capacity for n in self.nodes),
            'physical_size': physical_size,
        }

        vcluster_info = Cluster.objects.regular().aggregate(
            allocated_size=Coalesce(Sum('size'), 0),
            count=Count('*'))

        volumes = sx.listVolumes()['volumeList']
        post_replica = None if nodes_down else \
            sum(n.used_space for n in self.nodes)
        disk_usage = {
            'pre_replica': sum(v['usedSize'] for v in volumes.values()),
            'post_replica': post_replica,
        }

        return {
            'nodes_down': nodes_down,
            'cluster': cluster,
            'vcluster_info': vcluster_info,
            'disk_usage': disk_usage,
        }

    def get_nodes_context(self):
        # Group nodes by their zone
        has_zones = any(n.zone is not None for n in self.nodes)
        context = {'has_zones': has_zones}
        if has_zones:
            context['zones'] = group_by_zone(self.nodes)
        else:
            context['nodes'] = self.nodes
        return context

    def get_context_data(self, **kwargs):
        context = {}
        context.update(self.get_cluster_context())
        context.update(self.get_nodes_context())
        context.update(kwargs)
        return super(SuperAdminHomeView, self).get_context_data(**context)


def group_by_zone(nodes):
    """Group nodes by their zone."""
    zones = {}
    for node in nodes:
        zone_nodes = zones.setdefault(node.zone, [])
        zone_nodes.append(node)

    # Order zones by name, zoneless at the end
    zones = sorted(zones.items(), key=lambda i: (i[0] is None, i[0]))
    zones = OrderedDict(zones)
    return zones


@super_admin_only
class StatsView(generic.TemplateView):
    template_name = 'stats.html'
    title = _("Statistics")
    url_name = 'stats'


@super_admin_only
class GetStatsView(generic.View):
    """Return stats for a given time range."""
    url_name = 'get_stats'

    def get(self, request, *args, **kwargs):

        def _get(key):
            return int(self.request.GET.get(key)) / 1000
        try:
            from_, till_ = _get('from'), _get('till')
        except (TypeError, ValueError):
            return JsonResponse({}, status=400)

        fetcher = StatsFetcher(from_, till_)
        stats = fetcher.fetch_all_stats()
        return JsonResponse(stats)


class TaskViewMixin(object):
    model = TaskMeta

    def get_queryset(self):
        return self.model.objects.visible_to(self.request.user)


class TaskListView(TaskViewMixin, generic.ListView):
    template_name = 'task_list.html'
    context_object_name = 'task_list'
    paginate_by = 25
    url_name = 'task_list'
    title = _("Recent tasks")


class TaskStatusView(TaskViewMixin, generic.DetailView):
    template_name = 'task_status.html'
    url_name = 'task_status'
    title = _("Task status")
    pk_url_kwarg = 'uuid'

    def get_object(self):
        """Catch invalid UUID exception."""
        try:
            return super(TaskStatusView, self).get_object()
        except ValueError:
            raise Http404()

    def get_context_data(self, **kwargs):
        task_status_init = json.dumps({'uuid': str(self.object.id)})
        return super(TaskStatusView, self).get_context_data(
            task_status_init=task_status_init, **kwargs)
