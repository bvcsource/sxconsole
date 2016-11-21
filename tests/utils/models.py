# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from datetime import datetime, timedelta

from model_mommy.mommy import make

from sxconsole.accounts.models import PasswordReset


def test_token_manager_expired(db):
    now = datetime.now()
    week = timedelta(days=7)

    valid = make(PasswordReset, expiration_date=(now + week))
    assert valid in PasswordReset.objects.all()
    assert valid not in PasswordReset.objects.expired()

    expired = make(PasswordReset, expiration_date=(now - week))
    assert expired not in PasswordReset.objects.all()
    assert expired in PasswordReset.objects.expired()
