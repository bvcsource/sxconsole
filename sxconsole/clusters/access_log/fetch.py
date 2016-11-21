# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from time import time

from sxconsole.celery import register_task, TaskMeta
from sxconsole.clusters.models import AccessLogEntryModel
from .download import download_logs_for_range
from .parse import user_ids


@register_task(TaskMeta.TYPES.PREPARE_ACCESS_LOGS)
def prepare_access_log(self, from_, till, vcluster=None, volume=None,
                       user=None):
    print 'Preparing access logs...'

    now = time()
    user_ids.update()
    access_log = download_logs_for_range(from_, till)
    if vcluster:
        access_log = add_vcluster_context(access_log, vcluster)
    access_log = filter_access_log(access_log, volume=volume, user=user)
    print 'Fetching took {}s.'.format(round(time() - now, 2))

    now = time()
    access_log = list(access_log)
    print 'Parsing took {}s.'.format(round(time() - now, 2))

    now = time()
    store_results(access_log, self)
    print 'Saving took {}s.'.format(round(time() - now, 2))

    query = {
        'from': from_,
        'till': till,
        'vcluster': vcluster,
        'volume': volume,
        'user': user,
    }
    return {
        'query': query,
    }


def add_vcluster_context(access_log, vcluster):
    """Filter access log by vcluster and update its entries' volume
    attribute."""
    query = vcluster.lower() + '.'
    for entry in access_log:
        volume = entry['volume']
        if volume.lower().startswith(query):
            entry['volume'] = volume[len(query):]
            yield entry


def filter_access_log(access_log, volume=None, user=None):
    filters = [
        lambda e: e['operation'] != AccessLogEntryModel.OPERATIONS.LIST,
    ]
    if volume:
        volume_query = volume and volume.lower()
        filters.append(lambda e: volume_query in e['volume'].lower())
    if user:
        user_query = user and user.lower()
        filters.append(lambda e: user_query in e['user'].lower())

    for entry in access_log:
        if all(f(entry) for f in filters):
            yield entry


def store_results(access_log, task):
    task_id = task.request.id
    models = (AccessLogEntryModel(task_id=task_id, **e) for e in access_log)
    AccessLogEntryModel.objects.bulk_create(models, batch_size=100)
