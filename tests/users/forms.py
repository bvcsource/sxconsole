# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

from mock import Mock

from sxconsole.users.forms import UserForm


def get_form_errors(data):
    cluster = Mock(users=[])
    return UserForm(data, cluster=cluster).errors


class TestUserForm:
    def test_option_required(self):
        data = {
            'email': 'ffigiel@skylable.com',
        }
        assert 'option' in get_form_errors(data)

    def test_option_invalid(self):
        data = {
            'email': 'ffigiel@skylable.com',
            'option': 'yak-shaving',
        }
        assert 'option' in get_form_errors(data)

    def testoption_invite(self):
        data = {
            'email': 'ffigiel@skylable.com',
            'option': 'invite',
            'message': 'Some link: {{ link }}',
        }
        assert not get_form_errors(data)
