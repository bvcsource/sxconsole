# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
'''
'''

from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='Cluster name', validators=[django.core.validators.RegexValidator(b'^[a-zA-Z0-9-_.]+$')])),
                ('max_volumes', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('max_users', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('quota', models.PositiveIntegerField(null=True, blank=True)),
                ('admins', models.ManyToManyField(related_name='_clusters', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
