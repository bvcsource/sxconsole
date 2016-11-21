# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''
from __future__ import absolute_import

import pytest

from sxconsole.clusters.models import Cluster
from sxconsole.templatetags import sxconsole


class TestIcon:
    def test_invalid(self):
        with pytest.raises(TypeError):
            sxconsole.icon(object())

    def test_cluster(self, db):
        root = Cluster.objects.get()
        regular = Cluster.objects.create()

        regular_icon = sxconsole.icon(regular)
        assert 'fa-globe' not in regular_icon
        assert 'fa-server' in regular_icon

        root_icon = sxconsole.icon(root)
        assert 'fa-globe' in root_icon
        assert 'fa-server' not in root_icon
