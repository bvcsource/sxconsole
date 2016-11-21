# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

import pytest

from sxconsole.accounts.models import Admin, AdminLevels
from tests.factories import AdminFactory, ClusterFactory


@pytest.mark.parametrize('is_superadmin, level', [
    (False, AdminLevels.ADMIN),
    (True, AdminLevels.SUPER_ADMIN),
])
def test_admin_manager_visible_to(db, is_superadmin, level):
    me = AdminFactory(level=level)
    co_admin = AdminFactory()
    them = AdminFactory()
    admin_with_no_clusters = AdminFactory()

    ClusterFactory(admins=[me, co_admin])
    ClusterFactory(admins=[them])

    visible_admins = set(Admin.objects.visible_to(me))
    if is_superadmin:
        assert visible_admins == {me, co_admin, them, admin_with_no_clusters}
    else:
        assert visible_admins == {me, co_admin}
