# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20151103_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordreset',
            name='admin',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
