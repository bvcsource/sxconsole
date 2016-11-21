# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


S3IMPORT = 101


def merge_task_tables(apps, schema_editor):
    ClusterTask = apps.get_model('clusters', 'ClusterTask')
    TaskMeta = apps.get_model('sxconsole', 'TaskMeta')
    for old in ClusterTask.objects.all():
        new = TaskMeta.objects.create(
            id=old.id, cluster_id=old.cluster_id, admin_id=old.owner_id,
            type=S3IMPORT)
        new.queue_date = old.start_date
        new.save()
        old.delete()


def split_task_tables(apps, schema_editor):
    ClusterTask = apps.get_model('clusters', 'ClusterTask')
    TaskMeta = apps.get_model('sxconsole', 'TaskMeta')
    for old in TaskMeta.objects.filter(type=S3IMPORT):
        new = ClusterTask.objects.create(
            id=old.id, cluster_id=old.cluster_id, owner_id=old.admin_id)
        new.start_date = old.queue_date
        new.save()
        old.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0023_clustertask_owner'),
        ('sxconsole', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(merge_task_tables, split_task_tables)
    ]
