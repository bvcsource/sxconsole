# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import sxconsole.accounts.models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20151103_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='admin',
            name='level',
            field=models.IntegerField(default=1, verbose_name='Level', choices=sxconsole.accounts.models.AdminLevels),
        ),
    ]
