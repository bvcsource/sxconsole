# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from mock import patch

from sxconsole.accounts.models import Admin, PasswordReset


def test_admin_create_or_invite__existing(user):
    with patch('sxconsole.accounts.models.send_mail') as send_mail:
        Admin.get_or_invite(user.email)
    assert not PasswordReset.objects.filter(admin=user).exists()
    assert send_mail.call_args is None


def test_admin_create_or_invite__new(db):
    email = 'user@example.com'

    with patch('sxconsole.accounts.models.send_mail') as send_mail:
        Admin.get_or_invite(email)
        send_mail_args = send_mail.call_args[0]

    assert Admin.objects.filter(email=email).exists()
    assert PasswordReset.objects.filter(admin__email=email).exists()
    assert email in send_mail_args
