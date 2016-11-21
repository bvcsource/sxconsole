# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import sxconsole.core
import sizefield.models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0017_auto_20160120_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='size',
            field=sizefield.models.FileSizeField(default=0, help_text='e.g. 100GB', verbose_name='Size', validators=[sxconsole.core.size_validator]),
        ),
    ]
