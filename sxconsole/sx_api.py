# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''
from collections import namedtuple
from logging import getLogger
from time import time

from django.conf import settings
from django.utils.functional import SimpleLazyObject
from sxclient import Cluster, UserData, SXController, SXFileCat, SXFileUploader


logger = getLogger(__name__)

Version = namedtuple('Version', 'major, minor, released')


def logged_calls(func):
    """Decorator for logging api calls."""
    def wrapped(*args, **kwargs):
        operation = func.im_class.__name__
        start = time()
        result = func(*args, **kwargs)
        total = time() - start

        if total > 0.1:
            log = logger.warn if total > 1 else logger.debug
            log("({:.3f}) sx.{}".format(total, operation))
        return result
    return wrapped


def get_sx():

    class Api(object):
        """Provides a simplified sxclient experience."""

        def __init__(self, conf):
            self._cluster = self._get_cluster(conf)
            self._user_data = self._get_user_data(conf)
            self._sx = SXController(
                self._cluster, self._user_data,
                request_timeout=conf.get('request_timeout') or 5)

            for name in self._sx.available_operations:
                # Wrap api functions
                operation = getattr(self._sx, name)
                func = logged_calls(operation.json_call)
                func.__doc__ = operation.__doc__
                func.call_on_node = logged_calls(operation.call_on_node)
                setattr(self, name, func)

            self.downloader = SXFileCat(self._sx)
            self.uploader = SXFileUploader(self._sx)

        def get_cluster_uuid(self):
            return self._sx.get_cluster_uuid()

        def _get_user_data(self, conf):
            if 'admin_key' in conf:
                return UserData.from_key(conf['admin_key'])
            elif 'admin_key_path' in conf:
                return UserData.from_key_path(conf['admin_key_path'])
            else:
                raise ValueError(
                    "You must provide either 'admin_key' or 'admin_key_path' "
                    "in the sx config.")

        def _get_cluster(self, conf):
            ip_addresses = conf.get('ip_addresses')
            if isinstance(ip_addresses, basestring):
                ip_addresses = [ip_addresses]
            kwargs = {
                'name': conf.get('cluster'),
                'ip_addresses': ip_addresses,
                'is_secure': conf.get('is_secure', True),
                'port': conf.get('port'),
                'verify_ssl_cert':
                conf.get('certificate') or conf.get('verify_ca')
            }
            return Cluster(**kwargs)

        def get_sx_version(self):
            node_ip = self.listNodes()['nodeList'][0]
            version = self.getNodeStatus(node_ip)['libsxclientVersion']
            return parse_sx_version(version)

        @property
        def has_indexer(self):
            from sxconsole.core import _index_user_names
            return _index_user_names.issubset(self.listUsers())

        @property
        def has_encryption(self):
            version = self.get_sx_version()
            return version.major >= 2

        @property
        def has_volume_rename(self):
            version = self.get_sx_version()
            return version >= (2, 1, False)

        @property
        def has_volume_replica_change(self):
            version = self.get_sx_version()
            return version >= (2, 1, False)

    return Api(settings.SX_CONF)


def parse_sx_version(version):
    """Parse a `maj.min-commit` version string. Presence of commit indicates
    that this is not an official release."""
    try:
        version, commit = version.split('-')
    except ValueError:
        commit = None
    major, minor = map(int, version.split('.'))

    return Version(major, minor, not commit)

sx = SimpleLazyObject(get_sx)
