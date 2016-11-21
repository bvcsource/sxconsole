# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models

from sxconsole.core import _root_cluster_name


def forwards(apps, schema_editor):
    Cluster = apps.get_model('clusters', 'Cluster')
    Cluster.objects.create(name=_root_cluster_name)


def backwards(apps, schema_editor):
    Cluster = apps.get_model('clusters', 'Cluster')
    Cluster.objects.get(name=_root_cluster_name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0010_cluster__settings'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
