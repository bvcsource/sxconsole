# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import pytest

from sxconsole.entities import IndexingModes
from sxconsole.utils.clusters import create_volume


def compare_responses(result, get):
    """
    Compares volume data from POST/PUT result with data from GET response.

    These should be identical, with the exception of some fields.
    """
    exclude = {'used_size'}

    def filter(d):
        return {k: v for k, v in d.items() if k not in exclude}
    assert filter(result) == filter(get)


def volume_url(cluster, volume=None):
    url = '/api/v1/clusters/{}/volumes/'.format(cluster.pk)
    if volume:
        url += '{}/'.format(volume)
    return url


def add_volume(cluster, name, **kwargs):
    """Util for easily creating some volume in given cluster."""
    kwargs.setdefault('size', 1024 ** 3)
    kwargs.setdefault('replicas', 1)
    kwargs.setdefault('revisions', 1)
    create_volume(cluster, name, **kwargs)


def test_invalid_cluster_pk(user, cluster, api_client):
    user.clusters.add(cluster)
    url = '/api/v1/clusters/{}/volumes/'.format(cluster.name)
    assert api_client.get(url, status=404)


class TestVolumeList:
    def test_authenticated_only(self, cluster, api_client):
        api_client.logout()
        url = volume_url(cluster)
        api_client.get(url, status=401)

    def test_empty(self, user, cluster, api_client):
        user.clusters.add(cluster)
        url = volume_url(cluster)
        assert api_client.get(url).data['volumes'] == []

    def test_list(self, user, api_client, cluster):
        user.clusters.add(cluster)
        vol_name = 'my_volume'
        vol_replicas = 2
        add_volume(cluster, vol_name, replicas=vol_replicas)
        url = volume_url(cluster)
        resp_volumes = api_client.get(url).data['volumes']
        assert len(resp_volumes) == 1

        resp = resp_volumes[0]
        assert resp['name'] == vol_name
        assert resp['replicas'] == vol_replicas


@pytest.mark.parametrize('has_access', [True, False])
def test_volume_detail(user, cluster, api_client, has_access):
    volume, replicas = 'my_volume', 2
    url = volume_url(cluster, volume)
    add_volume(cluster, volume, replicas=replicas)
    if has_access:
        user.clusters.add(cluster)
        resp = api_client.get(url).data
        assert resp['name'] == volume
        assert resp['replicas'] == replicas
    else:
        api_client.get(url, status=404)


class TestVolumeCreate:

    @pytest.fixture
    def data(self, has_indexer):
        return {
            'name': 'my_volume',
            'size': '2G',
            'replicas': 2,
            'revisions': 5,
            'encryption': True,
            'indexing': IndexingModes.FILENAMES,
        }

    @pytest.mark.parametrize('has_access', [True, False])
    def test_valid(self, data, user, cluster, api_client, has_access):
        url = volume_url(cluster)
        url_to_vol = volume_url(cluster, data['name'])
        if has_access:
            user.clusters.add(cluster)
            resp = api_client.post(url, data).data
            compare_responses(resp, api_client.get(url_to_vol).data)
            assert resp['name'] == data['name']
            assert resp['size'] == 2 * 1024 ** 3
            assert resp['indexing'] == data['indexing']
        else:
            api_client.post(url, data, status=404)

    def test_max_volumes(self, data, user, add_cluster, api_client):
        cluster = add_cluster(max_volumes=1)
        add_volume(cluster, 'limit_reached')
        user.clusters.add(cluster)
        url = volume_url(cluster)
        resp = api_client.post(url, data, status=403).data
        assert 'max volumes' in resp['detail']

    def test_name(self, data, user, cluster, api_client):
        user.clusters.add(cluster)
        url = volume_url(cluster)
        name = data['name'].upper()
        data['name'] = name
        # Should be lowercase
        resp = api_client.post(url, data).data
        assert resp['name'] == name.lower()
        # Should error - volume exists
        # Name should be case-insensitive
        resp = api_client.post(url, data, status=400).data
        assert any('exists' in e for e in resp['name'])

    def test_size(self, data, user, add_cluster, api_client):
        cluster_size = 1024 ** 3  # 1GB
        cluster = add_cluster(size=cluster_size)
        data['size'] = cluster_size + 1
        user.clusters.add(cluster)
        url = volume_url(cluster)
        resp = api_client.post(url, data, status=400).data
        assert any('smaller size' in e for e in resp['size'])

    def test_replicas(self, data, user, add_cluster, api_client):
        """
        Should ignore user-specified replica count and apply cluster's replica
        count.
        """
        cluster_replicas = 2
        cluster = add_cluster(replicas=cluster_replicas)
        data['replicas'] = cluster_replicas + 1
        user.clusters.add(cluster)
        url = volume_url(cluster)
        resp = api_client.post(url, data).data
        assert resp['replicas'] == cluster_replicas


@pytest.mark.parametrize('has_access', [True, False])
def test_volume_update(user, super_user, cluster, api_client, has_indexer,
                       has_access):
    volname = 'my_volume'
    new_volname = 'my_renamed_volume'
    revisions = 2
    new_revisions = 3
    replicas = 3
    new_replicas = 4
    new_indexing = IndexingModes.CONTENT

    url = volume_url(cluster, volname)
    new_url = volume_url(cluster, new_volname)
    add_volume(cluster, volname, revisions=revisions, replicas=replicas)

    # Load volume data
    api_client.force_authenticate(super_user)
    data = api_client.get(url).data
    api_client.force_authenticate(user)

    # Prepare test data
    data['name'] = new_volname
    data['revisions'] = new_revisions
    data['replicas'] = new_replicas
    data['indexing'] = new_indexing

    if has_access:
        user.clusters.add(cluster)
        # Update volume
        resp = api_client.put(url, data).data
        assert resp['name'] == new_volname
        assert resp['revisions'] == new_revisions
        assert resp['replicas'] == new_replicas
        assert resp['indexing'] == new_indexing
        compare_responses(resp, api_client.get(new_url).data)
    else:
        # Post as an unauthorized user & check results
        api_client.put(url, data, status=404)
        api_client.force_authenticate(super_user)
        resp = api_client.get(url).data
        assert resp['name'] != new_volname
        assert resp['revisions'] != new_revisions
        assert resp['replicas'] != new_replicas
        assert resp['indexing'] != new_indexing


@pytest.mark.parametrize('has_access', [True, False])
def test_volume_delete(user, cluster, api_client, has_access):
    volume = 'my_volume'
    url = volume_url(cluster, volume)
    add_volume(cluster, volume)
    if has_access:
        user.clusters.add(cluster)
        api_client.delete(url)
        api_client.get(url, status=404)
    else:
        api_client.delete(url, status=404)
