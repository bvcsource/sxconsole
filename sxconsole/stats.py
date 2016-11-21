# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import math
import os
from collections import namedtuple
from operator import itemgetter

import whisper
from django.conf import settings

from sxconsole.utils.sx import get_configuration_nodes


NODE_STATS = {
    'loadavg',
    'mem_free',
    'mem_used',
    'disk_free',
    'disk_usage',
    'network_in',
    'network_out',
}
CLUSTER_STATS = {'space_usage'}

CUMULATIVE_STATS = {
    'network_in',
    'network_out',
}


def _get_timestamps(args):
    ts = ['x']
    ts.extend(i * 1000 for i in xrange(*args))
    return ts


class StatsFetcher(object):

    def __init__(self, from_, till_):
        self.from_ = from_
        self.till_ = till_

    def fetch_all_stats(self):
        data = {s: self.fetch_stat(s)
                for s in (CLUSTER_STATS | NODE_STATS)}
        return data

    def fetch_stat(self, stat_name):
        if stat_name in CLUSTER_STATS:
            fetcher = self.fetch_cluster_stat
        elif stat_name in NODE_STATS:
            fetcher = self.fetch_nodes_stat
        else:
            raise ValueError('No such stat: {}'.format(stat_name))

        try:
            data = fetcher(stat_name)
        except (TypeError, whisper.InvalidTimeInterval):
            return []

        data = self.postprocess_stat(stat_name, data)
        return data

    def fetch_cluster_stat(self, stat):
        range_args, data = self.fetch(stat)

        timestamps = _get_timestamps(range_args)
        data.insert(0, stat)

        columns = [timestamps, data]
        return columns

    def fetch_nodes_stat(self, stat):
        columns = []
        for node in self.nodes:
            range_args, data = self.fetch(stat, node['uuid'])
            data.insert(0, node['ip'])
            columns.append(data)

        timestamps = _get_timestamps(range_args)
        columns.insert(0, timestamps)
        return columns

    def fetch(self, *parts):
        path = settings.CARBON_CONF['whisper_dir']
        path = os.path.join(path, *parts)
        path += '.wsp'
        range_args, values = whisper.fetch(
            path, fromTime=self.from_, untilTime=self.till_)
        return range_args, values

    def postprocess_stat(self, stat_name, data):
        processor = StatsProcessor(self.from_, self.till_)

        if stat_name in CUMULATIVE_STATS:
            data = processor.compress_columns(data, 100)
            data = derivative_map(data)
        else:
            data = processor.compress_columns(data, 50)

        processor.adjust_timestamps(data)
        return data

    @property
    def nodes(self):
        if not hasattr(self, '_nodes'):
            node_models = get_configuration_nodes()
            nodes = ({'ip': node['nodeAddress'], 'uuid': node['nodeUUID']}
                     for node in node_models)
            self._nodes = sorted(nodes, key=itemgetter('ip'))
        return self._nodes


class StatsProcessor(object):

    def __init__(self, from_, till_):
        self.from_ = from_
        self.till_ = till_

    def compress_columns(self, columns, max_len):
        return compress_columns(columns, max_len)

    def adjust_timestamps(self, columns):
        """
        Ensure that border timestamps are exactly the ones that have been
        requested.
        """
        timestamps, values = split_columns(columns)

        current_from = timestamps[1]
        target_from = self.from_ * 1000
        if target_from > current_from:
            timestamps[1] = target_from
        else:
            timestamps.insert(1, target_from)
            for v in values:
                v.insert(1, None)

        current_till = timestamps[-1]
        target_till = self.till_ * 1000
        if target_till < current_till:
            timestamps[-1] = target_till
        else:
            timestamps.append(target_till)
            for v in values:
                v.append(None)


def compress_columns(columns, max_len):
    compressed = []
    for c in columns:
        label = c.pop(0)
        c = compress_list(c, max_len)
        c.insert(0, label)
        compressed.append(c)
    return compressed


def compress_list(l, max_len):
    compressed = []
    for chunk in chunks(l, max_len):
        chunk = [n for n in chunk if n is not None]
        if chunk:
            mean = sum(chunk, 0.0) / len(chunk)
        else:
            mean = None
        compressed.append(mean)
    return compressed


def derivative_map(columns):
    """Convert column values into their derivatives."""
    timestamps, values = split_columns(columns)

    # Copy labels
    derivative_values = [[v[0]] for v in values]

    for i in xrange(1, len(timestamps) - 1):
        time_segment = pick_segment(timestamps, i)
        dt = get_dt(time_segment)
        for j, column in enumerate(derivative_values):
            value_segment = pick_segment(values[j], i)
            value = get_derivative(value_segment, dt)
            column.append(value)

    timestamps.pop(1)  # There's no derivative for first timestamp
    return [timestamps] + derivative_values


def get_dt(segment):
    return (segment.right - segment.left) / 1000  # Convert delta to seconds


def get_dv(segment):
    return max(segment.right - segment.left, 0)  # No negative speeds


def get_derivative(segment, dt):
    if None in segment:
        return None
    return get_dv(segment) / dt


Segment = namedtuple('Segment', ['left', 'right'])


def pick_segment(values, i):
    return Segment(values[i], values[i + 1])


def chunks(l, num):
    """Yield `num` chunks from `l`."""
    size = int(math.ceil(float(len(l)) / num))
    for i in xrange(0, len(l), size):
        yield l[i:i + size]


def split_columns(columns):
    timestamps, values = columns[0], columns[1:]
    return timestamps, values
