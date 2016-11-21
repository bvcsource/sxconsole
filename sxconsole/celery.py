# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''
from __future__ import absolute_import

import os
from functools import wraps
from logging import getLogger

from celery import Celery
from django.conf import settings
from django.utils import timezone
from django.utils.functional import SimpleLazyObject


logger = getLogger(__name__)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'sxconsole.settings.development',
)

TaskMeta = SimpleLazyObject(
    lambda: __import__('sxconsole.models', fromlist=['TaskMeta']).TaskMeta)

app = Celery('sxconsole')
app.config_from_object(settings)
app.autodiscover_tasks(lambda: settings.CELERY_TASK_SOURCES)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


def register_task(func_or_choice):
    if isinstance(func_or_choice, basestring) and \
            func_or_choice in TaskMeta.TYPES.values:
        task = _register_task_with_type(func_or_choice)
    elif hasattr(func_or_choice, '__call__'):
        task = _register_task_func(func_or_choice)
    else:
        raise TypeError("Unsupported type: {}"
                        .format(type(func_or_choice)))
    return task


def _register_task_func(func):
    """Decorator for registering celery tasks."""

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        _set_start_date(self.request.id)
        return func(self, *args, **kwargs)
    task = app.task(bind=True)(wrapped)
    return task


def _register_task_with_type(task_type):
    def decorator(func):
        task = _register_task_func(func)

        def run(admin, *args, **kwargs):
            celery_task = task.delay(*args, **kwargs)
            TaskMeta.objects.create(type=task_type, id=celery_task.id,
                                    admin=admin)
            return celery_task
        return run
    return decorator


def _set_start_date(task_id):
    """Updates `start_date` for given `TaskMeta` id."""
    try:
        task_meta = TaskMeta.objects.get(id=task_id)
        task_meta.start_date = timezone.now()
        task_meta.save()
    except Exception:
        logger.error(
            'Failed to set `start_date` for task {}'.format(task_id),
            exc_info=True,
        )


class TaskFailed(Exception):
    """Raised to indicate a failure within a task."""
    pass
