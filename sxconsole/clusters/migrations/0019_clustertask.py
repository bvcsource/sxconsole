# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0018_auto_20160126_1622'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterTask',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True)),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('cluster', models.ForeignKey(to='clusters.Cluster')),
            ],
        ),
    ]
