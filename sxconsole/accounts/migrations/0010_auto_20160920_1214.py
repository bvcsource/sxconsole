# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-20 12:14
from __future__ import unicode_literals

from django.db import migrations


LEVEL_MAP = {
    '1': 'ADMIN',
    '2': 'SUPER_ADMIN',
    '3': 'ROOT_ADMIN',
}


def forwards(apps, schema_editor):
    Admin = apps.get_model('accounts', 'Admin')
    for old, new in LEVEL_MAP.items():
        Admin.objects \
            .filter(level=old) \
            .update(level=new)


def backwards(apps, schema_editor):
    Admin = apps.get_model('accounts', 'Admin')
    for old, new in LEVEL_MAP.items():
        Admin.objects \
            .filter(level=new) \
            .update(level=old)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20160920_1214'),
    ]

    operations = [
        migrations.RunPython(
            forwards,
            backwards,
        ),
    ]
