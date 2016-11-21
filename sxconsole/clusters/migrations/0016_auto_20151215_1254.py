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
        ('clusters', '0015_clusterexpiration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='_settings',
            field=annoying.fields.JSONField(default={}, blank=True),
        ),
    ]
