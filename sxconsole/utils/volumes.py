# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import json

from boto.exception import S3ResponseError

from sxconsole.s3_api import s3
from sxconsole.sx_api import sx


def make_public(volume):
    policy = get_public_policy(volume)
    policy = json.dumps(policy)
    get_bucket(volume).set_policy(policy)


def make_private(volume):
    get_bucket(volume).delete_policy()


def is_public(volume):
    try:
        get_bucket(volume).get_policy()
        return True
    except S3ResponseError as e:
        if e.status != 404:
            raise
        return False


def get_bucket(name):
    bucket = s3.get_bucket(name)
    return bucket


def get_public_policy(volume):
    return {
        'Version': '2012-10-17',
        'Statement': [{
            'Sid': 'AddPerm',
            'Effect': 'Allow',
            'Principal': '*',
            'Action': ['s3:GetObject'],
            'Resource': ["arn:aws:s3:::%s/*" % volume],
        }],
    }


def update_volume(volume, data):
    kwargs = {}

    size = data['size']
    if size != volume.size:
        kwargs['size'] = size

    revisions = data['revisions']
    if revisions != volume.revisions:
        kwargs['maxRevisions'] = revisions

    new_volume_name = data.get('name')
    if sx.has_volume_rename and \
            new_volume_name and new_volume_name != volume.name:
        full_old_volume_name = volume.full_name
        full_new_volume_name = volume.cluster.build_name(new_volume_name)

        volume.name = new_volume_name
        volume.full_name = full_new_volume_name
        kwargs['newName'] = full_new_volume_name
    else:
        full_old_volume_name = volume.full_name

    if kwargs:
        sx.modifyVolume(full_old_volume_name, **kwargs)

    indexing = data.get('indexing')
    if indexing and sx.has_indexer:
        volume.set_indexing(indexing)

    if sx.has_volume_replica_change:
        new_replica = data.get('replicas')
        if new_replica and new_replica != volume.replicas:
            sx.changeVolumeReplica(volume.full_name, nextReplica=new_replica)
