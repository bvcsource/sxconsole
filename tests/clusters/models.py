# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

import pytest
from django.core.exceptions import ValidationError

from sxconsole import core
from sxconsole.clusters.models import Cluster


def test_cluster_queryset(cluster):
    assert Cluster.objects.regular().get() == cluster
    assert Cluster.objects.count() == 2


def test_cluster_properties(add_cluster):
    """Tests cluster.__str__ and default ordering."""
    names = 'cebad'  # Random order
    for name in names:
        add_cluster(name=name)
    assert map(str, Cluster.objects.regular()) == sorted(names)


def test_cluster_signals(cluster, api):
    assert cluster.name in api.listUsers()
    cluster.delete()
    assert cluster.name not in api.listUsers()


def test_validate_unique(db):
    """Cluster names should be case-insensitive and lowercased."""
    c = Cluster(name='FOObar', size=core._min_volume_size)
    c.full_clean()
    assert c.name == 'foobar'
    c.save()
    with pytest.raises(ValidationError):
        Cluster(name='fooBAR', size=core._min_volume_size).full_clean()


def test_cluster_delete(cluster, api):
    """Should handle the exception if the cluster-user doesn't exist."""
    # Rocking the boat
    api.removeUser(cluster.name)
    assert cluster.name not in api.listUsers()

    # This user doesn't exist, but the exception should be handled.
    cluster.delete()
    assert cluster.name not in api.listUsers()
