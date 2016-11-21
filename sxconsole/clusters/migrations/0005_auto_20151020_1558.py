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
        ('clusters', '0004_auto_20151020_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='max_users',
            field=models.PositiveSmallIntegerField(default=0, blank=True, validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='max_volumes',
            field=models.PositiveSmallIntegerField(default=0, blank=True, validators=[django.core.validators.MaxValueValidator(1000)]),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='quota',
            field=sizefield.models.FileSizeField(default=0, blank=True, validators=[django.core.validators.MinValueValidator(1048576)]),
        ),
    ]
