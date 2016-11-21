# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import sizefield.models
import sxconsole.core


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0018_auto_20160126_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='max_users',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Max users', validators=[django.core.validators.MaxValueValidator(65536)]),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='max_volumes',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Max volumes', validators=[django.core.validators.MaxValueValidator(65536)]),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='size',
            field=sizefield.models.FileSizeField(blank=True, help_text='e.g. 100GB', null=True, verbose_name='Size', validators=[sxconsole.core.size_validator]),
        ),
    ]
