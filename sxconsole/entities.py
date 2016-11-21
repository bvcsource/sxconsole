# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from collections import defaultdict
from operator import itemgetter

from dateutil.parser import parse as parse_date
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.functional import cached_property, SimpleLazyObject
from django.utils.translation import ugettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem
from sxclient.defaults import FILTER_NAME_TO_UUID
from sxclient.exceptions import SXClientException

from sxconsole import core
from sxconsole.sx_api import sx
from sxconsole.utils.sx import (
    split_zone, strip_zone, parse_zone_spec, invert_zones,
)
from sxconsole.utils.volumes import is_public


Cluster = SimpleLazyObject(
    lambda: __import__(
        'sxconsole.clusters.models',
        fromlist=['Cluster'],
    ).Cluster)


class IndexingModes(DjangoChoices):
    """Modes of volume indexing."""
    NO_INDEXING = ChoiceItem('NO_INDEXING', _("No"))
    FILENAMES = ChoiceItem('FILENAMES', _("Yes"))
    CONTENT = ChoiceItem('CONTENT', _("Full-text"))


class Volume(object):

    INDEXING_MODES = IndexingModes

    def __init__(self, cluster, full_name, data):
        namespace = data['volumeMeta'].get('namespace', '')
        if namespace and not cluster.is_root:
            prefix, name = core.split_name(full_name)
            if namespace != cluster.namespace or prefix != cluster.name:
                raise ValueError(
                    "This volume does not belong to this cluster!")
        else:
            name = full_name

        self.cluster = cluster
        self.full_name = full_name
        self.name = name
        self.prefix = namespace.decode('hex')

        self.size = data['sizeBytes']
        self.used_size = data['usedSize']
        self.revisions = data['maxRevisions']
        self.replicas = data['replicaCount']

        self.encryption = data['volumeMeta'].get('filterActive') == \
            FILTER_NAME_TO_UUID['aes256']

    @property
    def empty(self):
        return not self.used_size

    @cached_property
    def acl(self):
        """Filter volume acl to keep the cluster's users only."""
        acl = sx.getVolumeACL(self.full_name)
        acl = {k.lower(): v for k, v in acl.items()}

        volume_acl = []
        for user in self.cluster.users:
            email = user.email.lower()
            perms = set(acl.get(email, []))
            volume_acl.append({
                'email': email,
                'is_reserved': user.is_reserved,
                'read': 'read' in perms,
                'write': 'write' in perms,
                'manager': 'manager' in perms,
            })

        return sorted(volume_acl, key=itemgetter('email'))

    def get_user_acl(self, email):
        for perm in self.acl:
            if email.lower() == perm['email'].lower():
                return perm
        else:
            raise ValueError("No such user ({user}) in volume {volume}."
                             .format(user=email, volume=self.name))

    @cached_property
    def indexing(self):
        acl = sx.getVolumeACL(self.full_name)
        index_list = acl.get(core._index_list_user_name, [])
        index_all = acl.get(core._index_all_user_name, [])

        if 'read' in index_all:
            return IndexingModes.CONTENT
        elif 'read' in index_list:
            return IndexingModes.FILENAMES
        else:
            return IndexingModes.NO_INDEXING

    def get_indexing_display(self):
        return self.INDEXING_MODES.values[self.indexing]

    @cached_property
    def is_public(self):
        return is_public(self.full_name)

    def set_indexing(self, mode):
        index_list, index_all = get_indexing_mode_perms(mode)

        perms = defaultdict(list)
        perms[acl_read_key(index_list)].append(core._index_list_user_name)
        perms[acl_read_key(index_all)].append(core._index_all_user_name)

        sx.updateVolumeACL(self.full_name, perms)


def get_indexing_mode_perms(mode):
    """Return a two-tuple of boolean flags for sxindexer configuration.

    The flags indicate whether to grant (True) or revoke (False) read
    permissions for sxindexer-list and sxindexer-all users.
    """
    if mode == IndexingModes.NO_INDEXING:
        return False, False
    if mode == IndexingModes.FILENAMES:
        return True, False
    if mode == IndexingModes.CONTENT:
        return False, True


def acl_read_key(enable):
    '''
    >>> acl_read_key(True)
    'grant-read'
    >>> acl_read_key(False)
    'revoke-read'
    '''
    return 'grant-read' if enable else 'revoke-read'


class User(object):

    def __init__(self, cluster, email, data):

        cluster_names = core.get_user_cluster_names(data)
        if cluster.name not in cluster_names and not cluster.is_root:
            raise ValueError("This user does not belong to this cluster!")

        self.cluster = cluster
        self.email = email
        self.quota = data['userQuota']
        self.quota_used = data['userQuotaUsed']

        try:
            validate_email(self.email)
            self.has_valid_email = True
        except ValidationError:
            self.has_valid_email = False

    @property
    def is_reserved(self):
        username = self.email
        if '@' in username:
            return False
        return \
            username in core._reserved_user_names or \
            username.startswith('libres3-') or \
            Cluster.objects.filter(name__iexact=username).exists()


class Node(object):

    def __init__(self, cluster_data=None, node_data=None,
                 zone=None,
                 operation_status=None):
        n = node_data or {}
        c = cluster_data or {}

        if not n and not c:
            raise ValueError("At least one of cluster_data or node_data "
                             "is required.")

        self.zone = zone
        self.operation_status = operation_status

        self.uuid = n.get('UUID') or c.get('nodeUUID')
        self.public_ip = n.get('address') or c.get('nodeAddress')
        self.private_ip = \
            n.get('internalAddress') or c.get('nodeInternalAddress')
        if self.private_ip == self.public_ip:
            self.private_ip = None

        # ClusterStatus-only fields
        self.capacity = c.get('nodeCapacity')

        self.down = not node_data
        self.faulty = 'i' in c.get('nodeFlags', '')

        # NodeStatus-only fields
        self.sx_version = n.get('libsxclientVersion')
        self.storage_path = n.get('nodeDir')
        self.cores = n.get('cores')
        self.memory = n.get('memTotal')
        self.used_space = n.get('storageUsed')

        # Complex attributes
        if n:
            self.system = n['osType'] + ' ' + n['osRelease']
            self.hashfs_version = n['hashFSVersion'].split()[-1]
            self.local_time = parse_date(n['localTime'])
            self.free_space = n['fsAvailBlocks'] * n['fsBlockSize']
        else:
            self.system = None
            self.hashfs_version = None
            self.local_time = None
            self.free_space = None

    @property
    def specification_string(self):
        parts = [self.capacity, self.public_ip, self.private_ip, self.uuid]
        spec = build_specification_string(parts)
        return spec

    @classmethod
    def nodes_from_distribution_model(cls, nodes):
        return [cls(cluster_data=n) for n in nodes]

    @classmethod
    def get_current_nodes(cls):
        return load_nodes_for_configuration(target=False)

    @classmethod
    def get_target_nodes(cls):
        return load_nodes_for_configuration(target=True)

    def serialize(self):
        if self.operation_status:
            operation = self.operation_status.serialize()
        else:
            operation = None
        return {
            'uuid': self.uuid,
            'publicIp': self.public_ip,
            'privateIp': self.private_ip,
            'sxVersion': self.sx_version,
            'capacity': self.capacity,
            'isDown': self.down,
            'isFaulty': self.faulty,
            'operation': operation,
            'zone': self.zone,
        }


class OperationStatus(object):

    def __init__(self, operation):
        self.complete = operation['isComplete']
        self.type = operation['opType']
        self.info = operation['opInfo']

    @classmethod
    def from_node_status(cls, status):
        try:
            operation = status['clusterStatus']['opInProgress']
        except KeyError:
            return None
        return cls(operation)

    def serialize(self):
        return {
            'complete': self.complete,
            'type': self.type,
            'info': self.info,
        }


def build_specification_string(parts):
    """Specification string is a 'size/ip/internal_ip/uuid' string."""
    def assure_string(s):
        if not isinstance(s, basestring):
            s = str(s)
        return s
    parts = (assure_string(p) for p in parts
             if p)  # Skip falsy internal IP
    return '/'.join(parts)


def load_nodes_for_configuration(target=False):
    model_index = -1 if target else 0

    status = get_leader_status()
    distribution_model = status['distributionModels'][model_index]
    node_models, zone_spec = split_zone(distribution_model)

    zone_nodes = parse_zone_spec(zone_spec)

    node_zones = invert_zones(zone_nodes)
    nodes = get_nodes(node_models, node_zones)
    return nodes


def get_nodes(node_models, node_zones):
    nodes = []
    for node_model in node_models:
        node_zone = node_zones.get(node_model['nodeUUID'])
        node = get_node(node_model, zone=node_zone)
        nodes.append(node)
    return nodes


def get_node(node_model, zone=None):
    ip = node_model['nodeAddress']
    operation_status = get_operation_status(ip)
    node_status = get_node_status(ip)

    node = Node(cluster_data=node_model,
                node_data=node_status,
                zone=zone,
                operation_status=operation_status)
    return node


def get_operation_status(ip):
    try:
        node_cluster_status = sx.getClusterStatus.call_on_node(ip).json()
        operation = OperationStatus.from_node_status(node_cluster_status)
    except SXClientException:
        operation = None
    return operation


def get_node_status(ip):
    try:
        node_status = sx.getNodeStatus(ip)
    except SXClientException:
        node_status = None
    return node_status


def get_leader_status():
    status = sx.getClusterStatus()
    try:
        leader_status = fetch_leader_status(status)
    except (ValueError, SXClientException):
        leader_status = status
    return leader_status['clusterStatus']


def fetch_leader_status(status):
    raft_status = status['raftStatus']
    cluster_status = status['clusterStatus']

    if raft_status['role'] == 'leader':
        leader_status = status
    else:
        leader_uuid = raft_status['leader']
        leader_status = fetch_cluster_status_for_uuid(leader_uuid,
                                                      cluster_status)
    return leader_status


def fetch_cluster_status_for_uuid(node_uuid, cluster_status):
    """
    Given node uuid and some cluster status, return cluster stauts reported by
    that node.
    """
    all_nodes = flatten(strip_zone(model) for model
                        in cluster_status['distributionModels'])
    (node_ip,) = (n['nodeAddress'] for n in all_nodes
                  if n['nodeUUID'] == node_uuid)
    cluster_status = sx.getClusterStatus.call_on_node(node_ip).json()
    return cluster_status


def flatten(iterable):
    for group in iterable:
        for item in group:
            yield item


class DistributionModel(object):
    def __init__(self, raw_model):
        nodes, zone_spec = split_zone(raw_model)
        self.nodes = Node.nodes_from_distribution_model(nodes)
        self.zone_spec = zone_spec
        self.zones = parse_zone_spec(self.zone_spec)
