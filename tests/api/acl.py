# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from tests.api.users import create_user
from tests.api.volumes import add_volume


def acl_url(cluster, volume, user=None):
    url = '/api/v1/clusters/{}/volumes/{}/acl/'.format(cluster.pk, volume)
    if user:
        url += '{}/'.format(user)
    return url


def test_volume_acl(user, cluster, api_client):
    user.clusters.add(cluster)
    email = 'user@example.com'
    volume, revisions = 'my_volume', 2
    add_volume(cluster, volume, revisions=revisions)
    create_user(cluster, email)
    url = acl_url(cluster, volume)

    # There's one user
    resp = api_client.get(url).data['acl']
    assert len(resp) == 1

    # This user doesn't have any rights to our volume, and it isn't reserved
    resp = resp[0]
    assert resp['email'] == email
    for key in 'read', 'write', 'manager', 'is_reserved':
        assert resp[key] is False

    # Test put
    url = acl_url(cluster, volume, email)
    data = {'read': True, 'write': True, 'manager': False}
    resp = api_client.put(url, data).data
    assert resp == api_client.get(url).data
    for key in data:
        assert resp[key] == data[key], key

    # Test patch
    resp = api_client.patch(url, {'write': False}).data
    assert resp == api_client.get(url).data
    assert resp['write'] is False

    # No access
    user.clusters.remove(cluster)
    api_client.get(url, status=404)
