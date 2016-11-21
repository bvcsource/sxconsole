# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import subprocess

from sxconsole.celery import register_task, TaskFailed
from sxconsole.core import sxconsole_alias, ensure_sxconsole_alias
from sxconsole.entities import build_specification_string
from sxconsole.models import TaskMeta
from sxconsole.sx_api import sx
from sxconsole.utils import sx as sx_utils


class BaseTask(object):
    task_type = None
    fields = ['nodes']
    subcommand = None

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs[field])

    def get_args(self):
        """Return a list of args for the command to run."""
        main_args = self.get_main_args()
        if self.subcommand is not None:
            main_args = [self.subcommand] + main_args
        args = build_sxadm_command(main_args)
        return args

    def queue(self, admin):
        celery_task = run_command.delay(self)
        TaskMeta.objects.create(
            type=self.task_type,
            id=celery_task.id,
            admin=admin,
        )
        return celery_task.id

    def get_main_args(self):
        return self.get_nodes_spec()

    def get_nodes_spec(self):
        return [build_node_spec(n) for n in self.nodes]


class ModifyClusterConfiguration(BaseTask):
    task_type = TaskMeta.TYPES.MODIFY_CLUSTER
    fields = ['nodes', 'zones']
    subcommand = '--modify'

    def get_main_args(self):
        nodes_spec = self.get_nodes_spec()
        zones_spec = self.get_zones_spec()
        if zones_spec == '':
            return nodes_spec
        return nodes_spec + [zones_spec]

    def get_zones_spec(self):
        return sx_utils.build_zone_spec(self.zones)


class MarkNodesAsFaulty(BaseTask):
    task_type = TaskMeta.TYPES.MARK_NODES_AS_FAULTY
    subcommand = '--set-faulty'


class ReplaceFaultyNodes(BaseTask):
    task_type = TaskMeta.TYPES.REPLACE_FAULTY_NODES
    subcommand = '--replace-faulty'


def get_node(uuid, nodes):
    """
    >>> from collections import namedtuple
    >>> n = namedtuple('Node', 'uuid')
    >>> nodes = [n('a'), n('b'), n('c')]
    >>> get_node('b', nodes)
    Node(uuid='b')
    >>> get_node('missing', nodes)
    Traceback (most recent call last):
        ...
    ValueError: ...
    """
    try:
        (node,) = (n for n in nodes if n.uuid == uuid)
    except ValueError:
        raise ValueError("No such node: {}".format(uuid))
    return node


@register_task
def run_command(self, task):
    """Runs a sxadm command tied to given `BaseTask` instance."""
    args = task.get_args()
    ensure_sxconsole_alias()
    try:
        return subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise TaskFailed(e.output)


@register_task(TaskMeta.TYPES.RESIZE_CLUSTER)
def resize_cluster(self, diff):
    sx.resizeCluster(diff)


def build_sxadm_command(main_args):
    """Wrap core_args for sxadm usage."""
    args = ['sxadm', 'cluster'] + main_args + [sxconsole_alias]
    return args


def build_node_spec(node):
    """Convert dict with node information into a node specification string."""
    return build_specification_string(
        [
            node['capacity'],
            node['publicIp'],
            node['privateIp'],
            node['uuid'],
        ],
    )
