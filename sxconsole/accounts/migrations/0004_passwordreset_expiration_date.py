# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
import sxconsole.core


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20151026_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='passwordreset',
            name='expiration_date',
            field=models.DateTimeField(default=sxconsole.core.token_expiration, editable=False),
        ),
    ]
