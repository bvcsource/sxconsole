# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from djcelery.models import TaskMeta as CeleryTaskMeta

from sxconsole.clusters.models import AccessLogEntryModel
from sxconsole.models import TaskMeta


class Command(BaseCommand):
    help = 'Removes heavy task results to free up database space.'

    def handle(self, *args, **kwargs):
        threshold = datetime.now() - timedelta(days=1)

        query = Q(queue_date__lt=threshold)
        query &= Q(type=TaskMeta.TYPES.PREPARE_ACCESS_LOGS)

        tasks = TaskMeta.objects.filter(query)
        task_ids = list(tasks.values_list('pk', flat=True))

        tasks.delete()
        CeleryTaskMeta.objects.filter(task_id__in=task_ids).delete()
        AccessLogEntryModel.objects.filter(task_id__in=task_ids).delete()
