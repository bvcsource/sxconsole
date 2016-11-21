# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import pickle
import socket
import struct
from contextlib import closing
from datetime import datetime
from enum import Enum
from logging import getLogger
from time import time, sleep

from django.core.mail import mail_admins
from django.core.management.base import BaseCommand
from sxclient.exceptions import SXClientException

from sxconsole.sx_api import sx


logger = getLogger(__name__)


class Health(Enum):
    OK = 'OK'
    FAILING = 'FAILING'


class Command(BaseCommand):
    help = \
        'Obtains nodes and cluster statistics and stores them in the database'

    def handle(self, *args, **kwargs):
        from django.conf import settings
        self.collect_interval = settings.STATS_CONF.get('collect_interval', 10)
        self.fail_tolerance = settings.STATS_CONF.get('fail_tolerance', 300)

        self.last_successful_run = time()
        self.health = Health.OK

        while True:
            self.collect_stats_loop()

    def collect_stats_loop(self):
        self.collect_stats()
        self.check_health()
        self.wait()

    def collect_stats(self):
        self.last_run = time()
        try:
            collect_and_send_stats()
        except Exception as e:
            logger.warn("Failed to collect stats:\n{}: {}"
                        .format(type(e).__name__, e))
        else:
            self.last_successful_run = time()

    def check_health(self):
        """Update self.health and send alert if neccessary."""
        since_last_successful_run = time() - self.last_successful_run
        is_failing = since_last_successful_run > self.fail_tolerance
        new_health = Health.FAILING if is_failing else Health.OK
        if self.health != new_health:
            self.health = new_health
            self.send_alert()

    def send_alert(self):
        """Send alert about the stats collector's health."""
        title = '[{}] SX Console stats collector'.format(self.health.name)
        if self.health == Health.OK:
            msg = "Stats are being collected again."
        elif self.health == Health.FAILING:
            msg = "No stats have been collected since {} (UTC)." \
                .format(datetime.fromtimestamp(self.last_successful_run))
        else:
            raise ValueError("Unknown Health type: {}".format(self.health))
        mail_admins(title, msg)

    def wait(self):
        """Calculate time till next stats collection and wait."""
        run_duration = time() - self.last_run
        sleep_duration = self.collect_interval - run_duration
        if sleep_duration > 0:
            sleep(sleep_duration)


def collect_and_send_stats():
    collected_at = int(time())
    stats = collect_stats()
    data = serialize_data(collected_at, stats)
    send_stats(data)


def send_stats(data):
    from django.conf import settings
    with closing(socket.socket()) as sock:
        sock.connect((
            settings.CARBON_CONF['carbon_host'],
            settings.CARBON_CONF['port']))
        sock.sendall(data)


def serialize_data(timestamp, stats):
    tuples = prepare_data(timestamp, stats)
    payload = pickle.dumps(tuples, protocol=pickle.HIGHEST_PROTOCOL)
    header = struct.pack('!L', len(payload))
    return header + payload


def prepare_data(timestamp, stats):
    data = []
    for path, value in stats.items():
        serialized = (path, (timestamp, value))
        data.append(serialized)
    return data


def collect_stats():
    nodes_stats = collect_nodes_stats()
    cluster_stats = collect_cluster_stats()
    stats = sum_dicts(nodes_stats, cluster_stats)
    return stats


def collect_nodes_stats():
    stats = {}
    for ip in sx.listNodes()['nodeList']:
        try:
            node_status = sx.getNodeStatus(ip)
        except SXClientException as e:
            logger.info(
                "Failed to collect stats for node {ip}.\nError: {e}"
                .format(ip=ip, e=e))
        else:
            uuid = node_status['UUID']
            node_stats = collect_node_stats(node_status)
            stats[uuid] = node_stats
    stats = normalize_stats(stats)
    return stats


def collect_node_stats(node):
    statistics = node['statistics']

    try:
        loadavg = statistics['loadavg']['1min']
    except KeyError:
        # Unavailable in SX 2.0
        loadavg = 0

    mem_free = node['memAvailable']
    mem_used = node['memTotal'] - mem_free

    disk_free = node['fsAvailBlocks'] * node['fsBlockSize']
    disk_usage = node['storageUsed']

    traffic = statistics['traffic']['serverZones']['_']
    network_in = traffic['inBytes']
    network_out = traffic['outBytes']

    stats = {
        'loadavg': loadavg,
        'mem_used': mem_used,
        'mem_free': mem_free,
        'disk_free': disk_free,
        'disk_usage': disk_usage,
        'network_in': network_in,
        'network_out': network_out,
    }
    return stats


def collect_cluster_stats():
    volumes = sx.listVolumes()['volumeList']
    space_usage = sum(v['usedSize'] for v in volumes.itervalues())

    stats = {
        'space_usage': space_usage,
    }
    return stats


def normalize_stats(multi_stats):
    """
    >>> normalize_stats({'uuid': {'name': 'value'}})
    {'name.uuid': 'value'}
    """
    output = {}
    for suffix, stats in multi_stats.items():
        for name, stat in stats.items():
            key = '.'.join([name, suffix])
            output[key] = stat
    return output


def sum_dicts(*dicts):
    """
    >>> result = sum_dicts({'a': 1}, {'b': 2}, {'b': 3, 'c': 4})
    >>> result == {'a': 1, 'b': 3, 'c': 4}
    True
    """
    output = {}
    for d in dicts:
        output.update(d)
    return output
