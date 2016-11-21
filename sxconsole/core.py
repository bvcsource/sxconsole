# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import json
import os
import re
import subprocess
from base64 import b64encode
from datetime import datetime, timedelta
from logging import getLogger
from random import randint
from tempfile import mkstemp
from uuid import UUID

from django.conf import settings
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from sizefield.utils import filesizeformat
from sxclient import UserData, SXController
from sxclient.defaults import FILTER_NAME_TO_UUID
from sxclient.exceptions import SXClientException

from sxconsole.sx_api import sx


logger = getLogger(__name__)


version = '0.9.0'
"""SX Console version"""


_sep = '.'
"""Namespace separator for volume names.

For example, a volume 'foo' in a virtual cluster 'bar' will be named 'foo:bar'.
"""

_key_len = 20
"""Length of a user key."""

KEY_PADDING = '\0\0'


_root_cluster_name = 'root'
"""Cluster name for objects that aren't linked to a vcluster."""

_admin_user_name = 'admin'
"""Username of an admin user."""

log_volname = 'sxmonitor'
"""Volume which stores logs."""

_index_list_user_name = 'sxindexer-list'
_index_all_user_name = 'sxindexer-all'
_index_user_names = {_index_list_user_name, _index_all_user_name}
"""Usernames related to file indexing."""

_reserved_user_names = _index_user_names | {_admin_user_name}

_min_volume_size = 1024 ** 2

_min_replica_count = max(settings.APP_CONF.get('min_replicas'), 1)


def build_name(cluster, volume):
    """Given a cluster and volume names, return a full volume name."""
    assert identifier_re.match(cluster), 'Invalid cluster name'
    assert identifier_re.match(volume), 'Invalid volume name'
    return '{}{}{}'.format(cluster, _sep, volume)


def split_name(volume_name):
    """Given a full volume name, return a (prefix, name) tuple."""
    cluster, volume = volume_name.split(_sep, 1)
    return cluster, volume


def add_vcluster_to_desc(cluster, user):
    """Given a vcluster and user data, return userDesc updated with the new
    vcluster."""
    desc = get_user_desc(user)
    names = desc['vc']
    if cluster.name not in names:
        names.append(cluster.name)
    return serialize_user_desc(desc)


def remove_vcluster_from_desc(cluster, user):
    """Given a vcluster and user data, return userDesc with the vcluster name
    removed."""
    desc = get_user_desc(user)
    names = desc['vc']
    try:
        names.remove(cluster.name)
    except ValueError:
        pass
    return serialize_user_desc(desc)


def get_user_cluster_names(user):
    """Given a user data dict, return their virtual cluster names."""
    names = get_user_desc(user)['vc']
    return names


def get_user_volumes(username):
    key = get_user_key(username)
    user_sx = SXController(sx._sx.cluster, UserData.from_key(key))
    volumes = user_sx.listVolumes.json_call(includeMeta=True,
                                            includeCustomMeta=True)
    return volumes


def get_user_key(username):
    data = sx.getUser(username)
    id = data['userID'].decode('hex')
    key = data['userKey'].decode('hex')
    return build_token(id, key)


def build_token(id, key):
    """
    >>> id, key = 'a' * 20, 'b' * 20
    >>> b64encode(id + key + KEY_PADDING) == build_token(id, key)
    True
    """
    token = b64encode(id + key + KEY_PADDING)
    return token


def get_user_desc(user):
    try:
        desc = json.loads(user['userDesc'])
    except (KeyError, TypeError, ValueError):
        desc = {}
    if desc.get('vc'):
        desc['vc'] = desc['vc'].split(',')
    else:
        desc['vc'] = []
    return desc


def serialize_user_desc(desc):
    if desc.get('vc'):
        desc['vc'] = ','.join(desc['vc'])
    else:
        desc.pop('vc', None)
    return json.dumps(desc)


def create_key(email, password):
    """Convert given data to a sx-usable auth key."""
    uuid = sx.get_cluster_uuid()
    key = UserData.from_userpass_pair(email, password, uuid).key
    return key[20:40].encode('hex')  # Return private part only


identifier_re = re.compile(r'^[a-zA-Z0-9-_]{2,}$')
"""Regex for cluster and volume names."""


identifier_validator = validators.RegexValidator(
    identifier_re,
    message=_(
        "Name should consist of at least two characters and include "
        "only alphanumeric characters, hyphen and underscore."))

max_objects_validator = validators.MaxValueValidator(2 ** 16)


password_validator = validators.MinLengthValidator(8)


def size_validator(value):
    if value < _min_volume_size:
        raise ValidationError(_("Size must be at least 1MB."))


def replicas_validator(value):
    nodes_count = len(sx.listNodes()['nodeList'])
    if value < _min_replica_count or value > nodes_count:
        raise ValidationError(
            _("Replicas must be between {min} and {max}.")
            .format(min=_min_replica_count, max=nodes_count))


def revisions_validator(value):
    """
    >>> revisions_validator(65)
    Traceback (most recent call last):
        ...
    ValidationError: ...
    >>> revisions_validator(0)
    Traceback (most recent call last):
        ...
    ValidationError: ...
    >>> revisions_validator(8)
    """
    min, max = 1, 64
    if value < min or value > max:
        raise ValidationError(
            _("Revisions must be between {min} and {max}.")
            .format(min=min, max=max))


def port_validator(value):
    min, max = 0, 65535
    if value < min or value > max:
        raise ValidationError(
            _("Port number must be between {min} and {max}.")
            .format(min=min, max=max))


def token_expiration():
    """Generate an expiration date for a token."""
    return datetime.now() + timedelta(days=2)


def random_bytes(length):
    """Returns a random binary string.

    For convenience, it's already hex-encoded to work with sxclient.
    """
    bytes = (chr(randint(0, 255)) for i in range(length))
    return ''.join(bytes).encode('hex')


def generate_user_key():
    """Generate a random user key."""
    return random_bytes(20)


def generate_encryption_meta():
    """Returns volumeMeta dict for encrypted volumes."""
    meta = {
        'filterActive': 'aes256',  # SXClient replaces this with the uuid
    }
    uuid = FILTER_NAME_TO_UUID['aes256']
    uuid = str(UUID(uuid))  # Insert dashes
    cfg_key = '{}-cfg'.format(uuid)
    meta[cfg_key] = random_bytes(17)
    return meta


_invalid_volume_size_re = re.compile(r'.* between (\d+) and (\d+)')
_invalid_cluster_size_re = re.compile(r'.* requires a minimum of (\d+) bytes')


def get_exception_msg(e):
    """Executed when an exception occurs in views.

    Exception message will be checked against known errors, and a prepared
    message will be returned to the user.
    If it isn't a known error, log the message since it might've not been
    handled properly.

    Returns an error message.
    """
    msg = None

    if isinstance(e, SXClientException):
        msg = get_sxclient_exception_msg(e)
    elif isinstance(e, subprocess.CalledProcessError):
        msg = get_subprocess_exception_msg(e)

    if msg is None:
        logger.warning(
            "Unknown exception ocurred. "
            "The user will be shown a generic error message.\n"
            "Exception: {}".format(e))
        msg = _("An error occurred while processing your request. "
                "Please try again later.")
    return msg


def get_sxclient_exception_msg(e):
    msg = None
    error = e.message
    if 'Max retries exceeded' in error or \
            'Failed to query cluster' in error:
        msg = _("Connection to the cluster failed.")

    elif 'Invalid volume size' in error:
        match = _invalid_volume_size_re.match(error)
        if match:
            min_, max_ = match.groups()
            msg = _("Volume size should be between {min} and {max}.") \
                .format(min=filesizeformat(min_), max=filesizeformat(max_))
        elif error.endswith('reached cluster capacity'):
            msg = _("Can't create a new volume: "
                    "cluster capacity has been reached.")

    elif 'Invalid metadata value' in error:
        msg = _("Failed to update cluster metadata.")

    elif 'Invalid distribution' in error:
        match = _invalid_cluster_size_re.match(error)
        if match:
            min_ = match.groups()[0]
            msg = _("Cluster size should be at least {min}.") \
                .format(min=filesizeformat(min_))
    return msg


def get_subprocess_exception_msg(e):
    msg = None
    error = e.output

    op_failed = 'ERROR: Operation failed: '
    if error.startswith(op_failed):
        msg = error[len(op_failed):]
    return msg


sxconsole_alias = '@sxconsole'


def ensure_sxconsole_alias():
    fd, keyfile = mkstemp()
    # Store admin key in a tempfile
    with open(keyfile, 'w') as f:
        key = sx._sx._user_data.key.encode('base64')
        f.write(key)

    # Create alias for current sx configuration
    try:
        delete_alias(sxconsole_alias)  # Delete existing alias
        create_alias(sxconsole_alias, sx._sx.cluster, keyfile)
    finally:
        os.remove(keyfile)


def create_alias(alias, cluster, keyfile):
    # Prepare sxinit args
    cluster = sx._cluster
    host_list = ','.join(cluster.iter_ip_addresses())
    args = ['sxinit',
            '--batch-mode',  # Run in non-interactive mode
            '--alias=' + alias,
            '--auth-file=' + keyfile,
            '--host-list=' + host_list]

    if not cluster.is_secure:
        args.append('--no-ssl')

    if cluster.port:
        args.append('--port={}'.format(cluster.port))

    cluster_address = 'sx://admin@' + cluster.name
    args.append(cluster_address)
    # Run sxinit
    try:
        subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to create sxconsole alias:\n{}'
                     .format(e.output))
        raise


def delete_alias(alias):
    try:
        subprocess.check_output(['sxinit', '--delete', alias],
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        if not e.output.startswith('ERROR: Invalid SX URI'):
            logger.error('Failed to remove sxconsole alias:\n{}'
                         .format(e.output))
            raise
