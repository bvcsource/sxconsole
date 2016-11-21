# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clusters', '0008_auto_20151030_1808'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cluster',
            old_name='quota',
            new_name='size',
        ),
    ]
