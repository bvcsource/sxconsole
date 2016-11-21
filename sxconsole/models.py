# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from __future__ import absolute_import

from celery import states as celery_states
from celery.result import AsyncResult
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from djcelery.models import TaskMeta as CeleryTaskMeta
from djchoices import DjangoChoices, ChoiceItem

from sxconsole.utils.fields import ChoiceField


class TaskTypes(DjangoChoices):
    """Choices for a task type."""
    REMOVE_NODE = ChoiceItem('1', _("Remove node"))
    MARK_AS_FAULTY = ChoiceItem('2', _("Mark node as faulty"))
    REPLACE_FAULTY = ChoiceItem('3', _("Replace faulty node"))
    ADD_NODE = ChoiceItem('4', _("Add node"))
    EDIT_NODE = ChoiceItem('5', _("Modify node"))
    UPDATE_ZONES = ChoiceItem('6', _("Update zones"))
    RESIZE_CLUSTER = ChoiceItem('7', _("Resize cluster"))
    # Used in the new Cluster Management page:
    MODIFY_CLUSTER = ChoiceItem('8', _("Modify cluster configuration"))
    MARK_NODES_AS_FAULTY = ChoiceItem('9', _("Mark nodes as faulty"))
    REPLACE_FAULTY_NODES = ChoiceItem('10', _("Replace faulty nodes"))

    S3IMPORT = ChoiceItem('101', _("Import data from S3"))
    DELETE_VOLUME = ChoiceItem('102', _("Delete volume"))
    PREPARE_ACCESS_LOGS = ChoiceItem('103', _("Prepare access logs"))


class TaskMetaQuerySet(models.QuerySet):
    def visible_to(self, admin):
        if admin.is_superadmin:
            qs = self
        else:
            qs = self.filter(admin=admin)
        return qs


class TaskMeta(models.Model):
    """Contains additional metadata about a Celery task."""
    TYPES = TaskTypes

    id = models.UUIDField(primary_key=True)
    cluster = models.ForeignKey('clusters.Cluster', null=True)
    admin = models.ForeignKey('accounts.Admin', null=True)

    queue_date = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(null=True)

    type = ChoiceField(choices=TYPES)

    objects = TaskMetaQuerySet.as_manager()

    class Meta:
        ordering = ('-queue_date',)

    @cached_property
    def result(self):
        try:
            result = CeleryTaskMeta.objects.get(task_id=self.id)
        except CeleryTaskMeta.DoesNotExist:
            result = AsyncResult(self.id)
        return result

    @property
    def end_date(self):
        return getattr(self.result, 'date_done', None)

    @property
    def status(self):
        return self.result.status

    @property
    def ready(self):
        return self.status in celery_states.READY_STATES

    @property
    def info(self):
        result = self.result.result

        # Hide internal information provided by celery
        if self.status == celery_states.STARTED and \
                isinstance(result, dict) and \
                set(result.keys()) == {'hostname', 'pid'}:
            result = None
        return result
