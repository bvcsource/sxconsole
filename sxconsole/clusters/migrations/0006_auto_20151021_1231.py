# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import re
import django.core.validators
import sizefield.models
import sxconsole.core


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0005_auto_20151020_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='max_users',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(65536)]),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='max_volumes',
            field=models.PositiveSmallIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(65536)]),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='name',
            field=models.CharField(unique=True, max_length=50, verbose_name='Cluster name', validators=[django.core.validators.RegexValidator(re.compile(b'^[a-zA-Z0-9-_][a-zA-Z0-9-_.]+$'))]),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='quota',
            field=sizefield.models.FileSizeField(default=0, validators=[sxconsole.core.size_validator]),
        ),
    ]
