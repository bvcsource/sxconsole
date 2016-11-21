# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import re
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0016_auto_20151215_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='name',
            field=models.CharField(unique=True, max_length=50, verbose_name='Cluster name', validators=[django.core.validators.RegexValidator(re.compile(b'^[a-zA-Z0-9-_]{2,}$'), message='Name should consist of at least two characters and include only alphanumeric characters, hyphen and underscore.')]),
        ),
    ]
