# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

import subprocess

# Make sure celery is initialized during startup
from . import celery  # noqa


VERSION = (2, 0, 8)


def get_version():
    version = '.'.join(str(n) for n in VERSION)
    git_hash = get_git_hash()
    if git_hash is not None:
        version = '{} (@{})'.format(version, git_hash)
    return version


def get_git_hash():
    try:
        return subprocess.check_output([
            'git', 'rev-parse', '--short', 'HEAD',
        ]).strip()
    except subprocess.CalledProcessError:
        return None
