# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0012_auto_20151122_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='thin_provisioning',
            field=models.BooleanField(default=False, verbose_name='Thin provisioning'),
        ),
    ]
