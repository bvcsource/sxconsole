# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import sxconsole.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clusters', '0021_auto_20160205_1101'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskMeta',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True)),
                ('queue_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField(null=True)),
                ('type', models.IntegerField(choices=sxconsole.models.TaskTypes)),
                ('admin', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('cluster', models.ForeignKey(to='clusters.Cluster', null=True)),
            ],
        ),
    ]
