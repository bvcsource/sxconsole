# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from mock import Mock, patch

from sxconsole.volumes.validators import can_add_volume, validate_volume_size


def test_can_add_volume_expired():
    cluster = Mock()
    user = Mock()
    cluster.max_volumes = None
    cluster.is_expired = True

    user.is_superadmin = False
    can, msg = can_add_volume(cluster, user)
    assert can is False
    assert 'has expired' in msg

    user.is_superadmin = True
    can, msg = can_add_volume(cluster, user)
    assert can is True
    assert msg is None


def test_validate_volume_size():
    cluster = Mock()
    cluster.thin_provisioning = False
    old_size = 1
    max_size = 2

    with patch(
            'sxconsole.volumes.validators.clusters.get_free_size',
            return_value=max_size):
        valid, msg = validate_volume_size(cluster, max_size, old_size)
        assert valid is False
        assert 'running out of space' in msg

        valid, msg = validate_volume_size(cluster, max_size - 1, old_size)
        assert valid is True
        assert msg is None
