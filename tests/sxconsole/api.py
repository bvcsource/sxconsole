# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from __future__ import absolute_import

from sxconsole.sx_api import parse_sx_version


def test_parse_sx_version():
    version = parse_sx_version('2.1-f00')

    assert version == (2, 1, False)
    assert version.major == 2
    assert version.minor == 1
    assert version.released is False
    assert parse_sx_version('2.1') > parse_sx_version('2.1-f00')
