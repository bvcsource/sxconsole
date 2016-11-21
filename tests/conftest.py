# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''
from __future__ import absolute_import

import pytest

from sxconsole import core
from sxconsole.accounts.models import AdminLevels
from tests.utils import BetterAPIClient, mock_api
from . import factories


@pytest.fixture(autouse=True)
def api():
    """Mock api functions."""
    from sxconsole.sx_api import sx
    mock_api(sx)
    return sx


@pytest.fixture
def add_cluster(db):
    return factories.ClusterFactory


@pytest.fixture
def cluster(add_cluster):
    return add_cluster()


@pytest.fixture
def user(db):
    return factories.AdminFactory()


@pytest.fixture
def super_user(db):
    return factories.AdminFactory(level=AdminLevels.SUPER_ADMIN)


@pytest.fixture
def api_client(user):
    """Client for REST API."""
    client = BetterAPIClient()
    client.force_authenticate(user=user)
    return client


@pytest.yield_fixture
def has_indexer(api):
    for username in core._index_user_names:
        api.createUser(username)
    yield
    for username in core._index_user_names:
        api.removeUser(username)
