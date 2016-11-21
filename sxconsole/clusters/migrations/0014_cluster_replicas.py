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
        ('clusters', '0013_cluster_thin_provisioning'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='replicas',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Optional. If set, all new volumes in this cluster will use this replica count.', null=True, verbose_name='Replicas', validators=[sxconsole.core.replicas_validator]),
        ),
    ]
