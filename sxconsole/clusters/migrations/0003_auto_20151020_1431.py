# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import sizefield.models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0002_quota_sizefield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='quota',
            field=sizefield.models.FileSizeField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1048576)]),
        ),
    ]
