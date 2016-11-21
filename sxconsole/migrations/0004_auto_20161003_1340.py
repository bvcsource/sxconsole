# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-03 13:40
from __future__ import unicode_literals

from django.db import migrations
import sxconsole.utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sxconsole', '0003_auto_20160919_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskmeta',
            name='type',
            field=sxconsole.utils.fields.ChoiceField(choices=[(b'1', 'Remove node'), (b'2', 'Mark node as faulty'), (b'3', 'Replace faulty node'), (b'4', 'Add node'), (b'5', 'Modify node'), (b'6', 'Update zones'), (b'7', 'Resize cluster'), (b'8', 'Modify cluster configuration'), (b'9', 'Mark nodes as faulty'), (b'10', 'Replace faulty nodes'), (b'101', 'Import data from S3'), (b'102', 'Delete volume'), (b'103', 'Prepare access logs')], max_length=3),
        ),
    ]
