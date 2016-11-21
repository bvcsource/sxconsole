# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

from mock import Mock

from sxconsole.api.serializers import (
    TaskMetaSerializer, get_volume_serializer, get_new_volume_serializer,
)
from sxconsole.celery import TaskFailed


class TestWrappedVolumeSerializers:

    def test_no_indexing(self):
        assert 'indexing' not in get_volume_serializer()._declared_fields
        assert 'indexing' not in get_new_volume_serializer()._declared_fields

    def test_has_indexing(self, has_indexer):
        assert 'indexing' in get_volume_serializer()._declared_fields
        assert 'indexing' in get_new_volume_serializer()._declared_fields


class TestTaskMetaSerializer:

    def test_info(self):
        msg = 'This is an error message'
        f = TaskMetaSerializer().get_info

        task = Mock(info=TaskFailed(msg))
        assert f(task) == msg

        task = Mock(info=OSError(msg))
        assert f(task) == msg

        task = Mock(info=OSError(0, msg))
        assert f(task) == '[Errno 0] {}'.format(msg)
