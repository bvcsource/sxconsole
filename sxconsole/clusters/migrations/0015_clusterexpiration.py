# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import annoying.fields


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0014_cluster_replicas'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClusterExpiration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expiration_date', models.DateField(verbose_name='Expiration date')),
                ('user_permissions', annoying.fields.JSONField(default={})),
                ('cluster', models.OneToOneField(related_name='_expiration', verbose_name='Cluster', to='clusters.Cluster')),
            ],
        ),
    ]
