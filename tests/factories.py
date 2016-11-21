# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

import factory

from sxconsole.accounts.models import Admin
from sxconsole.clusters.models import Cluster


class AdminFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence('admin{}@example.com'.format)

    class Meta:
        model = Admin


class ClusterFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence('cluster_{}'.format)

    class Meta:
        model = Cluster

    @factory.post_generation
    def admins(self, create, extracted, **kwargs):
        if not create:
            return
        elif extracted:
            for admin in extracted:
                self.admins.add(admin)
