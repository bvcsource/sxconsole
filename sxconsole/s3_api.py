# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

import logging
import socket
from base64 import b64encode
from urlparse import urlparse

import boto
from django.utils.functional import SimpleLazyObject

from .sx_api import sx


logger = logging.getLogger(__name__)


def get_s3():

    def get_kwargs():
        meta = sx.getClusterMetadata()['clusterMeta']
        s3_addr = meta.get('libres3_address', '').decode('hex')
        s3_addr = urlparse(s3_addr)

        scheme = s3_addr.scheme
        host = s3_addr.netloc
        if not scheme or not host:
            return

        # Confirm that *.host domain names are registered too
        try:
            socket.gethostbyname(host)
            socket.gethostbyname('wildcard.' + host)
        except socket.gaierror:
            return

        kwargs = {
            'aws_access_key_id': 'admin',
            'aws_secret_access_key': b64encode(sx._user_data.key),
        }

        try:
            kwargs['is_secure'] = is_secure(scheme)
        except ValueError:
            logger.error("Unsupported libres3 url scheme: {}"
                         .format(scheme))
            return

        try:
            host, port = host.split(':')
            port = int(port)
        except ValueError:
            port = 443 if kwargs['is_secure'] else 80
        kwargs['port'] = port
        kwargs['host'] = host

        return kwargs

    class S3(object):

        def __init__(self, kwargs):
            self.is_available = bool(kwargs)
            if kwargs:
                self.connection = boto.connect_s3(**kwargs)

        def __getattr__(self, name):
            handler = self.connection if self.is_available else super(S3, self)
            return getattr(handler, name)

    kwargs = get_kwargs()
    return S3(kwargs)


def is_secure(scheme):
    if scheme == 'https':
        return True
    elif scheme == 'http':
        return False
    else:
        raise ValueError('Unknown url scheme')

s3 = SimpleLazyObject(get_s3)
