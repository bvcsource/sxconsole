# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import sxconsole.clusters.models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0026_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessLogEntryModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('task_id', models.UUIDField(db_index=True)),
                ('datetime', models.DateTimeField(db_index=True)),
                ('volume', models.TextField()),
                ('path', models.TextField()),
                ('operation', models.IntegerField(choices=sxconsole.clusters.models.AccessLogEntryOperation)),
                ('user', models.TextField()),
                ('ip', models.TextField()),
                ('user_agent', models.TextField()),
            ],
            options={
                'ordering': ['datetime'],
            },
        ),
        migrations.AlterIndexTogether(
            name='accesslogentrymodel',
            index_together=set([('task_id', 'datetime')]),
        ),
    ]
