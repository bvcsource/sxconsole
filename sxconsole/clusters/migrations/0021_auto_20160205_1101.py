# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0020_auto_20160204_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='max_users',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Max users', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65536)]),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='max_volumes',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Max volumes', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65536)]),
        ),
    ]
