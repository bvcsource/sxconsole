# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''
from __future__ import absolute_import

import json
from datetime import datetime, timedelta
from uuid import UUID

import pytest
from django.core.exceptions import ValidationError
from mock import Mock
from sxclient import UserData
from sxclient.defaults import FILTER_NAME_TO_UUID

from sxconsole import core
from sxconsole.clusters.models import Cluster


def test_build_name():
    with pytest.raises(AssertionError):
        core.build_name('foo.bar', 'foobar')  # Invalid cluster name
    with pytest.raises(AssertionError):
        core.build_name('foobar', 'foo.bar')  # Invalid cluster name
    assert core.build_name('foo', 'bar') == 'foo.bar', \
        "Should join cluster and volume names with a namespace separator."


def test_split_name():
    parts = 'foo', 'bar'
    full_name = 'foo.bar'
    assert core.split_name(full_name) == parts


class TestGetUserClusterName():

    def test_valid(self):
        """Should return a list of vcluster names."""
        user = {'userDesc': '{"vc": "vc1"}'}
        assert core.get_user_cluster_names(user) == ['vc1']
        user = {'userDesc': '{"vc": "vc1,vc2"}'}
        assert core.get_user_cluster_names(user) == ['vc1', u'vc2']

    def test_invalid(self):
        """Should return an empty list."""
        assert core.get_user_cluster_names({}) == []
        for desc in None, 'not a json', '{}', '{"vc": ""}':
            user = {'userDesc': desc}
            assert core.get_user_cluster_names(user) == []


def test_add_vcluster_to_desc():
    """Should update existing desc to include the new vcluster."""
    vc = Mock()
    vc.name = 'vcluster'
    u = {}
    assert core.add_vcluster_to_desc(vc, u) == '{"vc": "vcluster"}'

    u = {'userDesc': '{"vc": "other_vc"}'}
    new_desc = core.add_vcluster_to_desc(vc, u)
    assert json.loads(new_desc) == {'vc': 'other_vc,vcluster'}

    u = {'userDesc': '{"other_key": "value"}'}
    new_desc = core.add_vcluster_to_desc(vc, u)
    assert json.loads(new_desc) == {'vc': 'vcluster', 'other_key': 'value'}


def test_remove_vcluster_from_desc():
    """Should remove vcluster from the desc."""
    vc = Mock()
    vc.name = 'vcluster'
    u = {}
    assert core.remove_vcluster_from_desc(vc, u) == '{}'

    u = {'userDesc': '{"vc": "vcluster"}'}
    assert core.remove_vcluster_from_desc(vc, u) == '{}'

    u = {'userDesc': '{"vc": "vcluster,other"}'}
    assert core.remove_vcluster_from_desc(vc, u) == '{"vc": "other"}'

    u = {'userDesc': '{"other_key": "value"}'}
    assert core.remove_vcluster_from_desc(vc, u) == '{"other_key": "value"}'


def test_get_user_cluster_names():
    """Should always return a list."""
    u = {}
    assert core.get_user_cluster_names(u) == []
    u = {'userDesc': 'garbage'}
    assert core.get_user_cluster_names(u) == []
    u = {'userDesc': '{"vc": "a,b,c"}'}
    assert core.get_user_cluster_names(u) == ['a', 'b', 'c']


def test_get_user_desc():
    """Should include the `vc` list even if it's not present."""
    u = {}
    assert core.get_user_desc(u) == {'vc': []}
    u = {'userDesc': 'garbage'}
    assert core.get_user_desc(u) == {'vc': []}
    u = {'userDesc': '{"foo": "bar"}'}
    assert core.get_user_desc(u) == {'vc': [], 'foo': 'bar'}


def test_serialize_user_desc():
    desc = {'vc': [], 'foo': 'bar'}
    assert core.serialize_user_desc(desc) == '{"foo": "bar"}'

    desc = {'vc': ['vc1', 'vc2'], 'foo': 'bar'}
    serialized_desc = core.serialize_user_desc(desc)
    assert json.loads(serialized_desc) == {'vc': 'vc1,vc2', 'foo': 'bar'}


def test_create_key(api):
    username = 'foo'
    password = 'bar'
    key = UserData.from_userpass_pair(username, password,
                                      api.get_cluster_uuid()).key
    key = key[20:40].encode('hex')
    assert core.create_key(username, password) == key


def test_identifier_re():
    assert core.identifier_re.match('foo.bar') is None, \
        "Must not match the namespace separator."


class TestSizeValidator:
    """Should be valid for either 0 or at least 1mb"""

    @pytest.mark.parametrize('value', [1024 ** 2, 1024 ** 3])
    def test_valid(self, value):
        core.size_validator(value)

    @pytest.mark.parametrize('value', [-1, 0, 1024, 1024 ** 2 - 1])
    def test_invalid(self, value):
        with pytest.raises(ValidationError):
            core.size_validator(value)


def test_replicas_validator(api):
    """Replicas can't be greater than the number of nodes."""
    nodes_count = len(api.listNodes()['nodeList'])

    core.replicas_validator(1)
    core.replicas_validator(nodes_count)

    with pytest.raises(ValidationError):
        core.replicas_validator(0)
    with pytest.raises(ValidationError):
        core.replicas_validator(nodes_count + 1)


def test_revisions_validator():
    """Revisions must be between 1 and 64."""
    core.revisions_validator(1)
    core.revisions_validator(64)

    with pytest.raises(ValidationError):
        core.revisions_validator(0)
    with pytest.raises(ValidationError):
        core.revisions_validator(65)


def test_token_expiration():
    """Tokens shouldn't be valid for long periods of time."""
    now = datetime.now()
    expiration = core.token_expiration()
    assert now < expiration
    assert expiration < now + timedelta(days=7)


def test_random_bytes():
    """Should return a random hex-encoded binary string of given length."""
    length = 5
    bytes = core.random_bytes(length)
    assert len(bytes.decode('hex')) == length
    assert bytes != core.random_bytes(length)


def test_generate_user_key():
    """Should return a random 20-byte hex-encoded string."""
    key = core.generate_user_key()
    assert key != core.generate_user_key()
    decoded_key = key.decode('hex')
    assert len(decoded_key) == 20


def test_generate_encryption_meta():
    """Should return volumeMeta for aes256 filter."""
    meta = core.generate_encryption_meta()
    assert meta['filterActive'] == 'aes256'  # SXClient converts this to UUID
    uuid = FILTER_NAME_TO_UUID['aes256']
    uuid = str(UUID(uuid))  # Insert dashes
    cfg_key = '{}-cfg'.format(uuid)
    cfg_val = meta[cfg_key].decode('hex')
    assert len(cfg_val) == 17  # Must be 17 ran


def test_root_cluster(db):
    """A `root` cluster should exist once db is created."""
    cluster = Cluster.objects.get()
    assert cluster.is_root
    assert cluster.name == core._root_cluster_name
