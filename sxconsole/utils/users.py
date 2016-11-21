# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from sxconsole import core
from sxconsole.sx_api import sx
from sxconsole.users.models import UserPasswordReset


def add_user(cluster, email, password=None, quota=None):
    """Adds an existing user to the vcluster or creates a new user.

    Returns a bool which indicates if the user was created."""
    user = sx.listUsers().get(email)
    if user:
        update_user_vclusters(cluster, email, user, quota=quota)
        return False
    else:
        create_user(cluster, email, password, quota=quota)
        return True


def update_user_vclusters(cluster, email, user):
    desc = core.add_vcluster_to_desc(cluster, user)
    sx.modifyUser(email, desc=desc)


def create_user(cluster, email, password=None, quota=None):
    """Creates user in given vcluster."""
    key = core.create_key(email, password) if password \
        else core.generate_user_key()
    desc = {} if cluster.is_root else core.add_vcluster_to_desc(cluster, {})

    sx.createUser(email, userType='normal', userKey=key, desc=desc,
                  quota=quota)


def remove_user(username, cluster=None, force=False):
    if force:
        return delete_user(username)
    else:
        assert cluster is not None, \
            'Any of `cluster` or `force` arguments is required.'
        return remove_user_from_vcluster(username, cluster)


def delete_user(username):
    sx.removeUser(username)
    return True


def invite_user(email, cluster=None, template=None):
    if template is None:
        template = cluster.get_setting('invitation_message')
    else:
        assert template is not None, \
            'Any of `cluster` or `template` arguments is required.'
    return UserPasswordReset.objects.create(email=email) \
        .send_invitation(template)


def remove_user_from_vcluster(username, cluster):
    """Removes user from given virtual cluster by revoking permissions and
    updating userDesc.

    To prevent aggregation of stale users, user will be deleted if they have no
    other vclusters and volumes.
    """
    user_volumes = core.get_user_volumes(username)['volumeList']
    vc_volumes = filter_volumes_by_vcluster(user_volumes, cluster)
    user_data = sx.listUsers()[username]

    has_other_volumes = len(user_volumes) > len(vc_volumes)
    has_other_vclusters = \
        core.get_user_cluster_names(user_data) != [cluster.name]

    if has_other_volumes or has_other_vclusters:
        revoke_vcluster_permissions(vc_volumes, username)
        remove_vcluster_and_update(cluster, username, user_data)
    else:
        delete_user(username)


def filter_volumes_by_vcluster(volumes, cluster):
    output = []
    for name, volume in volumes.items():
        if volume['volumeMeta'].get('namespace') == cluster.namespace:
            output.append(name)
    return output


def revoke_vcluster_permissions(volumes, username):
    actions = ['revoke-read', 'revoke-write', 'revoke-manager']
    actions = {action: [username] for action in actions}
    for volume in volumes:
        sx.updateVolumeACL(volume, actions)


def remove_vcluster_and_update(cluster, username, user_data):
    new_desc = core.remove_vcluster_from_desc(cluster, user_data)
    sx.modifyUser(username, desc=new_desc)


def modify_user(user, data):
    kwargs = {
        'quota': data.get('quota'),
    }
    sx.modifyUser(user.email, **kwargs)
