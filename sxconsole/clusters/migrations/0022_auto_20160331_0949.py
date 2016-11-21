# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0021_auto_20160205_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='thin_provisioning',
            field=models.BooleanField(default=False, verbose_name='Enable thin provisioning'),
        ),
    ]
