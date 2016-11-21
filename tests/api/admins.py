# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

from tests.factories import AdminFactory


admins_url = '/api/v1/admins/'


def admin_url(admin=None):
    if admin is not None:
        return admins_url + '{}/'.format(admin.pk)


class TestAdminList:
    def test_authenticated_only(self, api_client):
        api_client.logout()
        api_client.get(admins_url, status=401)

    def test_empty(self, api_client):
        resp = api_client.get(admins_url).json()['admins']
        assert resp == []

    def test_list(self, user, super_user, api_client):
        api_client.force_authenticate(super_user)
        resp = api_client.get(admins_url).json()['admins']
        assert len(resp) == 2

        admin_data = next(a for a in resp if a['id'] == user.pk)
        assert admin_data['id'] == user.pk
        assert admin_data['email'] == user.email
        assert admin_data['level'] == user.level
        assert admin_data['level_display'] == user.get_level_display()


class TestAdminDetail:

    def test_invalid(self, user, api_client):
        url = admins_url + '0/'
        api_client.get(url, status=404)

    def test_valid(self, user, cluster, api_client):
        admin = AdminFactory()
        cluster.admins.add(user, admin)

        url = admin_url(admin)
        resp = api_client.get(url).json()
        assert resp['id'] == admin.pk
        assert resp['email'] == admin.email
        assert resp['level'] == admin.level
        assert resp['level_display'] == admin.get_level_display()
