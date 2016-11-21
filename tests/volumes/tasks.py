# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from mock import patch

from sxconsole.volumes.tasks import _delete_volume


def test_delete_volume():
    volume_name = 'test'
    with patch('sxconsole.volumes.tasks.sx') as sx:
        _delete_volume(None, volume_name)
    assert sx.deleteVolume.call_args == (
        (volume_name,),
        {'force': True},
    )
