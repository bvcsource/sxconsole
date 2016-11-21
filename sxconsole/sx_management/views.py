# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import json
import pipes
from collections import defaultdict

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from sxconsole.entities import Node
from sxconsole.sx_api import sx
from sxconsole.utils.decorators import super_admin_only
from sxconsole.utils.sx import get_configuration_nodes
from . import forms
from .cluster_operations import run_operations, get_heartbeat_params
from .tasks import sxadm as tasks


@super_admin_only
class ClusterManagementView(generic.FormView):
    template_name = 'cluster_management.html'
    title = _("Cluster Management")
    url_name = 'cluster_management'
    form_class = forms.ClusterManagementForm

    def get_context_data(self, **kwargs):
        nodes_init = self.get_nodes_init()
        return super(ClusterManagementView, self).get_context_data(
            nodes_init=nodes_init, **kwargs)

    def get_initial(self):
        meta = sx.getClusterMetadata()['clusterMeta']
        # Use the latest distribution model. If a task is in progress, don't
        # display current (i.e. stale) values
        nodes = get_configuration_nodes(target=True)
        cluster_size = sum(n['nodeCapacity'] for n in nodes)

        initial = {
            'cluster_size': cluster_size,
        }

        for key in ('sxweb_address', 'sxshare_address', 'libres3_address'):
            initial[key] = meta.get(key, '').decode('hex')

        initial.update(get_heartbeat_params())

        return initial

    def form_valid(self, form):
        if settings.DEMO:
            success = True
        else:
            success = run_operations(self, form)
        if success:
            return redirect(self.url_name)
        else:
            return self.form_invalid(form)

    def get_nodes_init(self):
        nodes = Node.get_target_nodes()
        nodes_init = {
            'nodeIds': [],
            'nodesById': {},
            'zoneNodes': defaultdict(list),
            'faultyNodesPresent': False,
            'rebalanceInProgress': False,
        }

        for n in nodes:
            nodes_init['nodeIds'].append(n.uuid)
            nodes_init['nodesById'][n.uuid] = n.serialize()
            nodes_init['zoneNodes'][n.zone or ''].append(n.uuid)

            if not nodes_init['faultyNodesPresent']:
                nodes_init['faultyNodesPresent'] = bool(n.faulty)

            if not nodes_init['rebalanceInProgress']:
                nodes_init['rebalanceInProgress'] = bool(n.operation_status)
        nodes_init['zoneNodes']['']  # NOQA # Ensure that the 'zoneless nodes' zone is present

        return json.dumps(nodes_init)


@super_admin_only
class SxadmBase(generic.View):
    """Base for cluster management operation views."""
    task_class = None
    task_fields = ['uuid']

    def get(self, *args, **kwargs):
        task = self.get_task()
        sxadm_args = self.get_shell_command(task)
        return JsonResponse({'args': sxadm_args})

    def post(self, *args, **kwargs):
        if settings.DEMO:
            task_status_url = reverse('cluster_management')
        else:
            celery_task_id = self.queue_task()
            task_status_url = reverse('task_status', args=[celery_task_id])
        return JsonResponse({'next': task_status_url})

    def queue_task(self):
        task = self.get_task()
        celery_task_id = task.queue(admin=self.request.user)
        return celery_task_id

    def get_task_kwargs(self):
        request_data = getattr(self.request, self.request.method)
        kwargs = json.loads(request_data['payload'])
        return kwargs

    def get_task(self):
        """Return a `BaseTask` instance here."""
        kwargs = self.get_task_kwargs()
        return self.task_class(**kwargs)

    def get_shell_command(self, task):
        args = map(pipes.quote, task.get_args())
        return ' '.join(args)


class MarkNodesAsFaultyView(SxadmBase):
    url_name = 'sxadm_mark_as_faulty'
    task_class = tasks.MarkNodesAsFaulty


class ReplaceFaultyNodesView(SxadmBase):
    url_name = 'sxadm_replace_faulty'
    task_class = tasks.ReplaceFaultyNodes


class ModifyClusterConfigurationView(SxadmBase):
    url_name = 'sxadm_modify_cluster'
    task_class = tasks.ModifyClusterConfiguration
