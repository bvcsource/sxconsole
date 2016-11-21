# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

import pytest
from mock import patch

from sxconsole.clusters.models import Cluster
from sxconsole.utils.users import create_user


def user_url(cluster, email=None):
    url = '/api/v1/clusters/{}/users/'.format(cluster.pk)
    if email:
        url += '{}/'.format(email)
    return url


class TestUserList:
    def test_authenticated_only(self, cluster, api_client):
        api_client.logout()
        url = user_url(cluster)
        api_client.get(url, status=401)

    def test_empty(self, user, cluster, api_client):
        user.clusters.add(cluster)
        url = user_url(cluster)
        assert api_client.get(url).data['users'] == []

    def test_list(self, user, api_client, cluster):
        user.clusters.add(cluster)
        email = 'user@example.com'
        create_user(cluster, email)
        url = user_url(cluster)
        resp_users = api_client.get(url).data['users']
        assert len(resp_users) == 1

        resp = resp_users[0]
        assert resp['email'] == email
        assert resp['is_reserved'] is False
        assert 'quota' in resp
        assert 'quota_used' in resp


@pytest.mark.parametrize('has_access', [True, False])
def test_user_detail(user, cluster, api_client, has_access):
    email = 'user@example.com'
    url = user_url(cluster, email)
    create_user(cluster, email)
    if has_access:
        user.clusters.add(cluster)
        resp = api_client.get(url).data
        assert resp['email'] == email
        assert 'quota' in resp
        assert 'quota_used' in resp
    else:
        api_client.get(url, status=404)


def test_is_reserved(super_user, cluster, api, api_client):
    api_client.force_authenticate(super_user)

    root = Cluster.objects.get(pk=1)
    assert root.is_root
    # url to vcluster's namespace-user
    url = user_url(root, cluster.name)
    resp = api_client.get(url).data
    assert resp['is_reserved'] is True
    assert 'quota' in resp
    assert 'quota_used' in resp


class TestUserCreate:

    @pytest.fixture
    def data(self):
        return {
            'email': 'user@example.com',
            'password': '12345678',
            'quota': 5 * 2 ** 20,
        }

    @pytest.yield_fixture
    def patch_invite_user(self):
        with patch('sxconsole.api.serializers.users.invite_user') as invite:
            yield invite

    @pytest.mark.parametrize('has_access', [True, False])
    def test_valid(self, data, user, cluster, api_client, patch_invite_user,
                   has_access):
        url = user_url(cluster)
        if has_access:
            user.clusters.add(cluster)
            assert patch_invite_user.called is False
            resp = api_client.post(url, data).data
            assert patch_invite_user.call_args == ((), {
                'email': data['email'],
                'cluster': cluster,
            })
            assert resp['email'] == data['email']
            assert resp['quota'] == data['quota']
        else:
            api_client.post(url, data, status=404)

    def test_max_users(self, data, user, add_cluster, api_client):
        cluster = add_cluster(max_users=1)
        create_user(cluster, 'limit_reached@example.com')
        user.clusters.add(cluster)
        url = user_url(cluster)
        resp = api_client.post(url, data, status=403).data
        assert 'max users' in resp['detail']

    def test_name(self, data, user, cluster, api_client):
        user.clusters.add(cluster)
        url = user_url(cluster)
        email = data['email'].upper()
        data['email'] = email
        # Should be lowercase
        resp = api_client.post(url, data).data
        assert resp['email'] == email.lower()
        # Should error - user exists
        # email should be case-insensitive
        resp = api_client.post(url, data, status=400).data
        assert any('already exists' in e for e in resp['email'])

    def test_quota(self, data, user, cluster, api_client):
        user.clusters.add(cluster)
        url = user_url(cluster)
        data['quota'] = 5
        resp = api_client.post(url, data, status=400).json()
        assert resp.keys() == ['quota']
        assert 'at least 1MB' in resp['quota'][0]


@pytest.mark.parametrize('has_access', [True, False])
def test_user_update(user, cluster, api_client, has_access):
    email = 'user@example.com'
    url = user_url(cluster, email)
    original_quota = 5 * 2 ** 20
    new_quota = 2 * original_quota
    create_user(cluster, email, quota=original_quota)
    if has_access:
        user.clusters.add(cluster)
        resp = api_client.patch(url, {'quota': new_quota}).json()
        assert resp['quota'] == new_quota
    else:
        api_client.patch(url, {}, status=404)


@pytest.mark.parametrize('has_access', [True, False])
def test_user_delete(user, cluster, api_client, has_access):
    email = 'user@example.com'
    url = user_url(cluster, email)
    create_user(cluster, email)

    fake_response = {'volumeList': {}}
    with patch('sxconsole.core.get_user_volumes', return_value=fake_response):
        if has_access:
            user.clusters.add(cluster)
            api_client.delete(url)
            api_client.get(url, status=404)
        else:
            api_client.delete(url, status=404)
