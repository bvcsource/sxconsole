# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

from datetime import datetime, timedelta

import pytest
from dateutil.parser import parse as parse_date

from sxconsole.clusters.models import Cluster, ClusterExpiration
from tests.factories import AdminFactory


def cluster_url(cluster):
    return '/api/v1/clusters/{}/'.format(cluster.pk)


def parse_expiration_date(resp):
    return parse_date(resp['expiration_date']).date()


@pytest.fixture
def expiration_date():
    return datetime.now().date() + timedelta(days=7)


class TestClusterList:
    def test_authenticated_only(self, api_client):
        api_client.logout()
        api_client.get('/api/v1/clusters/', status=401)

    def test_empty(self, api_client):
        assert api_client.get('/api/v1/clusters/').data['clusters'] == []

    def test_list(self, user, api_client, cluster):
        user.clusters.add(cluster)
        resp_clusters = api_client.get('/api/v1/clusters/').data['clusters']
        assert len(resp_clusters) == 1

        resp = resp_clusters[0]
        assert resp['id'] == cluster.pk
        assert resp['name'] == cluster.name


class TestClusterDetail:

    def test_invalid(self, user, api_client, cluster):
        url = cluster_url(cluster)
        api_client.get(url, status=404)

    def test_valid(self, user, api_client, cluster):
        user.clusters.add(cluster)
        url = cluster_url(cluster)
        resp = api_client.get(url).data
        assert resp['id'] == cluster.pk
        assert resp['name'] == cluster.name

    def test_expiration_date(self, user, cluster, api_client, expiration_date):
        user.clusters.add(cluster)
        url = cluster_url(cluster)

        resp = api_client.get(url).json()
        assert resp['expiration_date'] is None

        ClusterExpiration.objects.create(
            cluster=cluster,
            expiration_date=expiration_date,
        )
        resp = api_client.get(url).json()
        assert parse_expiration_date(resp) == expiration_date


class TestClusterCreate:

    def test_invalid_data(self, super_user, api_client):
        api_client.force_authenticate(super_user)
        api_client.post('/api/v1/clusters/', {}, status=400)

    def test_invalid_user(self, user, api_client):
        # Accessible to superadmins only
        api_client.post('/api/v1/clusters/', {'name': 'invalid'}, status=403)

    def test_valid(self, super_user, api_client):
        api_client.force_authenticate(super_user)
        resp = api_client.post('/api/v1/clusters/', {'name': 'cluster'}).data
        cluster = Cluster.objects.get(pk=resp['id'])
        assert cluster.name == resp['name']

    def test_expiration_date(self, super_user, api_client, expiration_date):
        test_data = {
            'name': 'cluster',
            'expiration_date': expiration_date.strftime('%Y-%m-%d'),
        }
        api_client.force_authenticate(super_user)
        resp = api_client.post('/api/v1/clusters/', test_data).json()
        assert parse_expiration_date(resp) == expiration_date

        cluster = Cluster.objects.get(pk=resp['id'])
        assert cluster.expiration.expiration_date == expiration_date


class TestClusterUpdate:

    def test_invalid_field(self, super_user, cluster, api_client):
        api_client.force_authenticate(super_user)
        url = cluster_url(cluster)
        data = api_client.get(url).data

        # Can't modify cluster name
        name = cluster.name
        data['name'] = 'invalid'
        api_client.put(url, data)
        cluster.refresh_from_db()
        assert cluster.name == name

    def test_invalid_user(self, user, super_user, cluster, api_client):
        url = cluster_url(cluster)
        api_client.get(url, status=404).data

        # Load cluster data
        api_client.force_authenticate(super_user)
        data = api_client.get(url).data
        api_client.force_authenticate(user)

        max_users = 5
        data['max_users'] = max_users
        api_client.put(url, data, status=403)
        cluster.refresh_from_db()
        assert cluster.max_users != max_users

    def test_valid(self, super_user, cluster, api_client):
        api_client.force_authenticate(super_user)
        url = cluster_url(cluster)
        data = api_client.get(url).data

        max_users = 5
        data['max_users'] = max_users
        api_client.put(url, data)
        cluster.refresh_from_db()
        assert cluster.max_users == max_users

    def test_expiration_date(self, super_user, cluster, api_client,
                             expiration_date):
        expiration = ClusterExpiration.objects.create(
            cluster=cluster,
            expiration_date=expiration_date,
        )
        api_client.force_authenticate(super_user)
        test_data = {'expiration_date': None}
        resp = api_client.patch(cluster_url(cluster), test_data).json()
        assert resp['expiration_date'] is None
        with pytest.raises(ClusterExpiration.DoesNotExist):
            expiration.refresh_from_db()


class TestClusterDelete:

    def test_invalid(self, cluster, api_client):
        url = cluster_url(cluster)
        api_client.delete(url, status=404)
        cluster.refresh_from_db()

    def test_valid(self, super_user, cluster, api_client):
        api_client.force_authenticate(super_user)
        url = cluster_url(cluster)
        api_client.delete(url)
        with pytest.raises(Cluster.DoesNotExist):
            cluster.refresh_from_db()


class TestClusterAdmins:

    def test_list_admins(self, user, cluster, api_client):
        cluster.admins.add(user)
        url = cluster_url(cluster) + 'admins/'
        resp = api_client.get(url, status=200)

        cluster_admins = resp.json()['cluster-admins']
        assert len(cluster_admins) == 1
        assert cluster_admins[0] == user.pk

    def test_add_admin(self, user, cluster, api_client):
        cluster.admins.add(user)
        new_admin = AdminFactory()
        url = cluster_url(cluster) + 'admins/{}/'.format(new_admin.pk)
        api_client.put(url, status=204, parse=False)

        admins = cluster.admins.all()
        assert len(admins) == 2
        assert set(admins) == {user, new_admin}

    def test_remove_admin(self, user, cluster, api_client):
        admin_to_remove = AdminFactory()
        cluster.admins.add(user)
        cluster.admins.add(admin_to_remove)
        url = cluster_url(cluster) + 'admins/{}/'.format(admin_to_remove.pk)
        api_client.delete(url, status=201)

        cluster.refresh_from_db()
        admins = cluster.admins.all()
        assert len(admins) == 1
        assert admins.get() == user
