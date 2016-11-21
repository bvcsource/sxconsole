# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0024_auto_20160225_1035'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clustertask',
            name='cluster',
        ),
        migrations.RemoveField(
            model_name='clustertask',
            name='owner',
        ),
        migrations.DeleteModel(
            name='ClusterTask',
        ),
    ]
