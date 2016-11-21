# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_userpasswordreset_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpasswordreset',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
