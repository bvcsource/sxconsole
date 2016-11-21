# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sxconsole', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='taskmeta',
            options={'ordering': ('-queue_date',)},
        ),
    ]
