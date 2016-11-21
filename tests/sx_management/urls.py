# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from sxconsole.sx_management.urls import get_urlpatterns


def test_sx_management_enabled(settings):
    settings.APP_CONF = {}
    assert get_urlpatterns() != []


def test_sx_management_disabled(settings):
    settings.APP_CONF = {'disable_sx_management': True}
    assert get_urlpatterns() == []
