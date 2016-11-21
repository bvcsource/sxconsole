# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''
from __future__ import absolute_import

from functools import wraps

import s3import
from boto.exception import S3ResponseError
from boto.https_connection import InvalidCertificateException
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.utils.translation import (
    ugettext_lazy as _, activate as activate_translation,
)

from sxconsole.clusters.models import Cluster
from sxconsole.sx_api import sx
from sxconsole.utils import clusters
from sxconsole.utils.mail import send_mail
from sxconsole.utils.strings import get_volume_naming_function


def send_s3import_status(func):
    """Send an S3 import status email when the wrapped function ends."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        recipient = kwargs.pop('email_address', None)

        source = ''
        destination = ''
        vcluster = ''
        try:
            source = join_host_and_port(
                kwargs.get('s3_host'), kwargs.get('s3_port'))
        except Exception:
            pass
        try:
            destination = join_host_and_port(
                settings.SX_CONF.get('cluster'), settings.SX_CONF.get('port'))
        except Exception:
            pass
        try:
            vcluster = Cluster.objects.get(pk=kwargs['cluster_pk']).name
        except Exception:
            pass

        try:
            returned = func(self, *args, **kwargs)

        except Exception as e:
            reason = ': '.join([type(e).__name__, str(e)])
            imported = None

            if hasattr(e, 'imported_buckets'):
                imported = e.imported_buckets
            else:
                imported = []
            if hasattr(e, 'skipped_buckets'):
                skipped = e.skipped_buckets
            else:
                skipped = []

            if recipient:
                finish_time = timezone.now()
                if timezone.is_aware(finish_time):
                    finish_time = timezone.localtime(finish_time)

                send_status_email(
                    recipients=recipient, succeeded=False,
                    uuid=self.request.id, time=finish_time, imported=imported,
                    skipped=skipped, reason=reason, source=source,
                    destination=destination, vcluster=vcluster)
            raise
        else:
            imported = returned.get('imported_buckets')
            skipped = returned.get('skipped_buckets')
            if recipient:
                finish_time = timezone.now()
                if timezone.is_aware(finish_time):
                    finish_time = timezone.localtime(finish_time)

                send_status_email(
                    recipients=recipient, succeeded=True, uuid=self.request.id,
                    time=finish_time, imported=imported, skipped=skipped,
                    source=source, destination=destination, vcluster=vcluster)
        return returned
    return wrapper


def send_status_email(**context):
    subject = _("S3 import {state_verb}")
    if context['succeeded']:
        subject = subject.format(state_verb=_("succeeded"))
    elif context['imported']:
        subject = subject.format(state_verb=_("partially failed!"))
    else:
        subject = subject.format(state_verb=_("failed!"))

    try:
        recipients = context.pop('recipients')
        send_mail(
            subject, recipients, template='mail/s3import_task.html',
            context=context)
    except Exception:
        pass


def join_host_and_port(host, port):
    filtered = filter(None, [host, port])
    stringed = map(str, filtered)
    joined = ':'.join(stringed)
    return joined


class CeleryTaskError(Exception):
    """Should be raised in case of a problem in a Celery task."""


class CeleryNonFatalTaskError(Exception):
    """
    Should be raised in case of a problem in a Celery task which can be
    ignored.
    """


@shared_task(bind=True)
@send_s3import_status
def import_from_s3(
        self, s3_host, s3_key_id, s3_secret_key, cluster_pk, replica_count,
        default_size=None, s3_port=None, s3_is_secure=True,
        s3_validate_certs=True, subdir=None, language=None):
    if language is not None:
        activate_translation(language)

    cluster = Cluster.objects.get(pk=cluster_pk)
    if replica_count is None:
        raise CeleryTaskError(
            _("Replica count is not set. Buckets will not be imported."))
    s3_context = s3import.S3ConnectionContext(
        host=s3_host,
        port=s3_port,
        access_key_id=s3_key_id,
        secret_access_key=s3_secret_key,
        is_secure=s3_is_secure,
        validate_certs=s3_validate_certs)

    owner = cluster.build_volume_owner()
    meta = cluster.build_volume_meta()

    s3importer = s3import.S3Importer(
        volume_size=default_size,
        volume_owner=owner,
        volume_replica=replica_count,
        volume_meta=meta,
        sx=sx._sx,
        s3_context=s3_context,
        subdir=subdir,
        worker_num=settings.S3IMPORT_THREAD_NUMBER)

    try:
        buckets = s3importer.get_bucket_names()
    except InvalidCertificateException as e:
        raise CeleryTaskError(str(e))
    get_volume_name = get_volume_naming_function()
    volumes = [get_volume_name(bucket) for bucket in buckets]

    imported = []
    skipped = []
    try:
        total_buckets = len(buckets)
        check_for_resources(cluster_pk, volumes)
        if default_size is not None:
            check_for_space(cluster_pk, volumes, default_size)
        for bucket, volume in zip(buckets, volumes):
            try:
                if volume in [item[1] for item in imported]:
                    raise CeleryNonFatalTaskError(_(
                        "Bucket '{}' will not be imported because its "
                        "destination volume name '{}' has already been "
                        "used.").format(bucket, volume))
                bucket_obj = s3importer.s3.get_bucket(bucket)
                self.update_state(state='PROGRESS',
                                  meta={'copied': len(imported),
                                        'skipped': len(skipped),
                                        'total': total_buckets,
                                        'current_from': bucket,
                                        'current_to': volume})
                volume_name = cluster.build_name(volume)

                required_space = s3importer.calculate_required_space(
                    bucket_obj, volume_name)
                if required_space == 0:
                    raise s3import.exceptions.S3NonFatalImportError(
                        _("Nothing to import for bucket '{}'").format(bucket))
                check_for_resources(cluster_pk, [volume])
                size = (
                    s3importer.volume_size or
                    s3import.tools.calculate_volume_size(required_space))
                check_for_space(cluster_pk, [volume], size)
                s3importer.check_quota(required_space, volume_name)
                s3importer.check_size(required_space, volume_name)

                self.update_state(state='PROGRESS',
                                  meta={'copied': len(imported),
                                        'skipped': len(skipped),
                                        'total': total_buckets,
                                        'current_from': bucket,
                                        'current_to': volume,
                                        'data_size': required_space})
                volume_created = s3importer.create_volume(volume_name, size)
                s3importer.copy_keys_parallelly(bucket_obj, volume_name)

                imported.append(
                    (bucket, volume, required_space, volume_created))

            except (
                    S3ResponseError, s3import.exceptions.S3NonFatalImportError,
                    CeleryNonFatalTaskError):
                skipped.append(bucket)

    except Exception as e:
        e.imported_buckets = imported
        e.skipped_buckets = skipped
        raise e

    return {'imported_buckets': imported, 'skipped_buckets': skipped}


def check_for_resources(cluster_pk, volumes):
    cluster = Cluster.objects.get(pk=cluster_pk)

    existing_volumes = set(volume.name for volume in cluster.volumes)
    volumes_after_import = set(volumes) | existing_volumes

    err_msg = ""
    if (cluster.max_volumes and
            len(volumes_after_import) > cluster.max_volumes):
        err_msg = _(
            "Volumes for imported buckets cannot be created because the max "
            "volumes limit would be exceeded. Buckets will not be imported.")
    elif cluster.is_expired:
        err_msg = _(
            "Buckets will not be imported because the cluster has expired.")
    if err_msg:
        raise CeleryTaskError(err_msg)


def check_for_space(cluster_pk, volumes, bucket_size):
    cluster = Cluster.objects.get(pk=cluster_pk)

    existing_volumes = set(volume.name for volume in cluster.volumes)
    new_volumes = set(volumes) - existing_volumes
    new_volumes_size = len(new_volumes) * bucket_size
    remaining_size = clusters.get_free_size(cluster)

    if (not cluster.thin_provisioning and
            cluster.size and
            remaining_size < new_volumes_size):
        if len(volumes) == 1:
            err_msg = _(
                "Volume '{}' cannot be created because there is not enough "
                "unallocated space on the cluster. Bucket will not be "
                "imported.").format(volumes[0])
        else:
            err_msg = _(
                "Volumes for imported buckets cannot be created because there "
                "is not enough unallocated space on the cluster. Buckets will "
                "not be imported.")
        raise CeleryTaskError(err_msg)
