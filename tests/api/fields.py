# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from datetime import date, timedelta

import pytest
from mock import Mock
from rest_framework import serializers

from sxconsole.api.serializers.fields import (
    validate_future_date, ClusterExpirationField,
)


def test_validate_future_date():
    today = date.today()
    one_day = timedelta(days=1)

    validate_future_date(today + one_day)
    validate_future_date(today)

    with pytest.raises(serializers.ValidationError):
        validate_future_date(today - one_day)


def test_cluster_expiration_field():
    field = ClusterExpirationField()
    assert validate_future_date in field.validators

    cluster = Mock()
    exp = cluster.expiration
    assert field.get_attribute(cluster) is exp
    assert field.to_representation(exp) is exp.expiration_date
    assert field.to_representation(None) is None
