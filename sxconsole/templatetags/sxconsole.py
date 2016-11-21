# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

from celery import states as celery_states
from django.template import Library
from django.utils.html import format_html

from sxconsole.clusters.models import Cluster
from sxconsole.entities import Volume
from sxconsole.models import TaskMeta


register = Library()


@register.filter(name='icon')
def icon(value, args=''):
    classes = ['fa'] + args.split()
    if isinstance(value, Cluster):
        if value.is_root:
            classes.append('fa-globe')
        else:
            classes.append('fa-server')
    elif isinstance(value, Volume):
        classes.append('fa-archive')
    else:
        raise TypeError(
            "Unknown type ({}) passed to `icon` filter."
            .format(type(value)))
    return format_html('<span class="{}"></span>', ' '.join(classes))


@register.simple_tag
def label_class(obj):
    modifier = _get_modifier_for_obj(obj)
    if modifier:
        cls = 'label label-' + modifier
    else:
        cls = None
    return cls


def _get_modifier_for_obj(obj):
    try:
        getter = _modifier_getters[type(obj)]
    except KeyError:
        raise TypeError("No modifiers for this type: {}"
                        .format(type(obj).__name__))
    else:
        modifier = getter(obj)
        return modifier


def _get_task_modifier(task):
    return _task_status_modifiers.get(task.status) or 'default'


_task_status_modifiers = {
    celery_states.SUCCESS: 'success',
    celery_states.FAILURE: 'danger',
    celery_states.STARTED: 'warning',
}


_modifier_getters = {
    TaskMeta: _get_task_modifier,
}
