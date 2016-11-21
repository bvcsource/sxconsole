# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


def forwards(apps, schema_editor):
    Cluster = apps.get_model('clusters', 'Cluster')
    Cluster.objects.filter(size=0).update(size=None)
    Cluster.objects.filter(max_volumes=0).update(max_volumes=None)
    Cluster.objects.filter(max_users=0).update(max_users=None)


def backwards(apps, schema_editor):
    Cluster = apps.get_model('clusters', 'Cluster')
    Cluster.objects.filter(size=None).update(size=0)
    Cluster.objects.filter(max_volumes=None).update(max_volumes=0)
    Cluster.objects.filter(max_users=None).update(max_users=0)


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0019_auto_20160204_1312'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards)
    ]
