# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import subprocess
from logging import getLogger

from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from sxclient.exceptions import SXClientException

from sxconsole.core import (
    get_exception_msg, sxconsole_alias, ensure_sxconsole_alias,
)
from sxconsole.sx_api import sx
from sxconsole.utils.dicts import selective_update
from .tasks.sxadm import resize_cluster


logger = getLogger(__name__)


class PartialFailure(Exception):
    """An operation failed, but we can continue."""

    def __init__(self, e):
        message = get_exception_msg(e)
        super(PartialFailure, self).__init__(message)


def run_operations(view, form):
    """Update cluster settings according to form data."""
    operations = [
        update_meta,
        queue_cluster_resize,
        update_heartbeat,
    ]
    for operation in operations:
        try:
            operation(view, form)
        except PartialFailure as e:
            form.add_error(None, e.message)
    return not form.errors


def update_meta(view, form):
    meta = sx.getClusterMetadata()['clusterMeta']
    data = form.cleaned_data

    new_meta = meta.copy()
    selective_update(new_meta, data, [
        'sxweb_address', 'sxshare_address', 'libres3_address'])
    if new_meta != meta:
        try:
            sx.setClusterMetadata(new_meta)
        except SXClientException as e:
            raise PartialFailure(e)


def queue_cluster_resize(view, form):
    diff = form.cleaned_data['cluster_size'] - form.initial['cluster_size']
    if diff:
        resize_cluster(view.request.user, diff)
        messages.info(view.request, _("Cluster resize has been scheduled."))


def update_heartbeat(view, form):
    changed_params = {}
    received, initial = form.cleaned_data, form.initial
    for key in HB_PARAMS:
        if received[key] != initial[key]:
            changed_params[key] = received[key]

    if changed_params:
        try:
            set_heartbeat_params(changed_params)
        except subprocess.CalledProcessError as e:
            raise PartialFailure(e)


HB_PARAMS = ('hb_keepalive', 'hb_warntime', 'hb_deadtime', 'hb_initdead')


def get_heartbeat_params():
    ensure_sxconsole_alias()
    args = ['sxadm', 'cluster', '--get-param', 'ALL', sxconsole_alias]
    try:
        output = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to read heartbeat params:\n{}'.format(e.output))
        output = ''
    return parse_heartbeat_params(output)


def parse_heartbeat_params(output):
    """
    >>> parse_heartbeat_params('hb_keepalive=20\\nhb_warntime=120\\nfoo=bar')
    {'hb_keepalive': 20, 'hb_warntime': 120}
    """
    params = {}
    for line in output.splitlines():
        if line.startswith(HB_PARAMS):
            key, value = line.split('=', 1)
            params[key] = int(value)
    return params


def set_heartbeat_params(params):
    ensure_sxconsole_alias()
    params = ['--set-param={}={}'.format(k, v) for k, v in params.items()]
    args = ['sxadm', 'cluster'] + params + [sxconsole_alias]
    subprocess.check_output(args, stderr=subprocess.STDOUT)
