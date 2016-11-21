# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from sxconsole.sx_api import sx


def split_zone(model):
    """Return (nodes, zone) tuple."""
    zone = model[-1]
    if isinstance(zone, basestring):
        model = model[:-1]
    else:
        zone = ''
    return model, zone


def strip_zone(model):
    """Return distribution model without the zone configuration."""
    nodes, zone = split_zone(model)
    return nodes


def parse_zone_spec(zone_spec):
    """Convert `zone_spec` into {zone: [uuid]} dict."""
    zone_map = {}
    if zone_spec:
        zone_specs = zone_spec.split(';')
        for spec in zone_specs:
            name, nodes = spec.split(':')
            nodes = nodes.split(',')
            zone_map[name] = nodes
    return zone_map


def build_zone_spec(zone_nodes):
    """Convert dict of zone nodes into a zone spec.

    >>> build_zone_spec({'c': ['1'], 'a': [], 'b': ['2', '3']})
    'b:2,3;c:1'
    """
    ordered_zones = sorted(zone_nodes.items())
    full_spec = []
    for zone, nodes in ordered_zones:
        if nodes:
            nodes_spec = ','.join(nodes)
            zone_spec = '{}:{}'.format(zone, nodes_spec)
            full_spec.append(zone_spec)
    return ';'.join(full_spec)


def invert_zones(zones):
    """Convert `zones` dict into {uuid: zone} dict."""
    inverted = {}
    for name, nodes in zones.items():
        for uuid in nodes:
            inverted[uuid] = name
    return inverted


def get_configuration(target=False):
    models = sx.getClusterStatus()['clusterStatus']['distributionModels']
    model_index = -1 if target else 0
    return models[model_index]


def get_configuration_nodes(target=False):
    """Return distribution model, but without the zone spec."""
    model = get_configuration(target)
    return strip_zone(model)
