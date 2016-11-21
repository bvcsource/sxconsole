# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import pprint
from logging import getLogger

from annoying.fields import JSONField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem
from sizefield.models import FileSizeField
from sizefield.utils import filesizeformat
from sxclient.exceptions import SXClientException, SXClusterNotFound

from sxconsole import core
from sxconsole.entities import Volume, User
from sxconsole.sx_api import sx
from sxconsole.utils.fields import ChoiceField


logger = getLogger(__name__)


_default_settings = {
    'invitation_message': '\n'.join([
        "You have been invited to {app_name}.".format(
            app_name=settings.SKIN['app_name']),
        "",
        "Click the link below to join:",
        "{{link}}"]),
}


class ClusterQuerySet(models.QuerySet):
    def regular(self):
        """Exclude the root cluster."""
        return self.exclude(name=core._root_cluster_name)


class Cluster(models.Model):
    """A fake cluster, within a physical cluster."""

    name = models.CharField(
        _("Cluster name"), max_length=50,
        validators=[core.identifier_validator], unique=True)

    max_volumes = models.PositiveSmallIntegerField(
        verbose_name=_("Max volumes"), validators=[MinValueValidator(1),
                                                   core.max_objects_validator],
        blank=True, null=True)
    max_users = models.PositiveSmallIntegerField(
        verbose_name=_("Max users"), validators=[MinValueValidator(1),
                                                 core.max_objects_validator],
        blank=True, null=True)
    size = FileSizeField(
        verbose_name=_("Size"),
        validators=[core.size_validator],
        null=True)
    thin_provisioning = models.BooleanField(
        verbose_name=_("Enable thin provisioning"), default=False)

    replicas = models.PositiveSmallIntegerField(
        verbose_name=_("Replicas"), help_text=_(
            "Optional. If set, all new volumes in this cluster will use "
            "this replica count."),
        validators=[core.replicas_validator], blank=True, null=True)

    _settings = JSONField(default={}, blank=True)
    """Customization store for the virutal cluster."""

    admins = models.ManyToManyField('accounts.Admin', related_name='_clusters')

    objects = ClusterQuerySet.as_manager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        self.name = self.name.lower()
        return super(Cluster, self).clean()

    def validate_unique(self, exclude=None):
        exclude = exclude or []
        errors = {}

        name = 'name'
        if name not in exclude:
            if Cluster.objects.filter(name__iexact=self.name).exists():
                errors[name] = self.unique_error_message(Cluster, [name])
        exclude.append(name)

        try:
            super(Cluster, self).validate_unique(exclude)
        except ValidationError as e:
            errors.update(e.error_dict)

        if errors:
            raise ValidationError(errors)

    def get_absolute_url(self):
        return reverse('cluster_detail', args=[self.pk])

    def get_setting(self, key):
        return self._settings.get(key) or _default_settings[key]

    def set_setting(self, key, value):
        if key not in _default_settings:
            raise ValueError("Unknown setting: {}".format(key))
        self._settings[key] = value
        self.save(update_fields=['_settings'])

    @property
    def is_root(self):
        """Root cluster groups all objects that don't have a vcluster."""
        return self.name == core._root_cluster_name

    @property
    def used_size(self):
        return sum(v.used_size for v in self.volumes)

    def get_used_size_display(self):
        usage = self.used_size
        size = self.size
        if size:
            percentage = int(round(100. * usage / size))
            return _("{usage} of {size} ({percentage}%)").format(
                usage=filesizeformat(usage), size=filesizeformat(size),
                percentage=percentage)
        else:
            return filesizeformat(usage)

    def get_allocated_size_display(self):
        allocated = sum(v.size for v in self.volumes)
        size = self.size
        if size:
            percentage = int(round(100. * allocated / size))
            return _("{usage} of {size} ({percentage}%)").format(
                usage=filesizeformat(allocated), size=filesizeformat(size),
                percentage=percentage)
        else:
            return filesizeformat(allocated)

    def build_name(self, volume_name):
        """Given a volume name, return a full volume name."""
        if self.is_root:
            return volume_name
        return core.build_name(self.name, volume_name)

    def build_volume_owner(self):
        update_user(self)  # Assure the user exists
        owner = core._admin_user_name if self.is_root else self.name
        return owner

    def build_volume_meta(self):
        return {} if self.is_root else {'namespace': self.namespace}

    @property
    def namespace(self):
        if not self.is_root:
            return self.name.encode('hex')

    @cached_property
    def volumes(self):
        """Get a list of volumes in this cluster."""
        def volume_belongs_to_cluster(namespace):
            if self.is_root:
                return True
            namespace = data['volumeMeta'].get('namespace')
            return namespace == self.namespace

        all_volumes = sx.listVolumes(includeMeta=True)['volumeList']
        volumes = [Volume(self, name, data)
                   for name, data in all_volumes.items()
                   if volume_belongs_to_cluster(data)]
        return sorted(volumes, key=lambda v: (v.prefix, v.name))

    def get_volume(self, name, refresh=False):
        """Return a volume based on the given name.

        If `refresh` is True, volumes cache will be reloaded first."""
        if refresh:
            try:
                del self.volumes
            except AttributeError:
                pass  # Cache was empty
        for volume in self.volumes:
            if volume.name == name:
                return volume
        raise ValueError('No such volume: {}'.format(name))

    def can_be_deleted(self):
        return not (self.volumes or self.users)

    @cached_property
    def users(self):
        """Get a list of users in this cluster.

        Unlike volumes, user emails are not prefixed with cluster name.
        """
        def user_belongs_to_cluster(user):
            if self.is_root:
                return True
            return self.name in core.get_user_cluster_names(user)

        all_users = sx.listUsers()
        users = [User(self, email, data)
                 for email, data in all_users.items()
                 if user_belongs_to_cluster(data)]
        return sorted(users, key=lambda u: (u.is_reserved, u.email))

    def get_user(self, email, refresh=False):
        """Return a user based on the given email.

        If `refresh` is True, users cache will be reloaded first."""
        if refresh:
            try:
                del self.users
            except AttributeError:
                pass  # Cache was empty
        for user in self.users:
            if user.email == email:
                return user
        raise ValueError('No such user: {}'.format(email))

    @property
    def expiration(self):
        try:
            return self._expiration
        except ClusterExpiration.DoesNotExist:
            return None

    @property
    def is_expired(self):
        exp = self.expiration
        return exp and exp.expiration_date <= timezone.now().date()


@receiver(pre_save, sender=Cluster)
def update_user(instance, **kwargs):
    """Create or update the virtual cluster user."""
    if instance.is_root:
        return
    user = sx.listUsers().get(instance.name)
    size = instance.size or 0
    if not user:
        sx.createUser(
            instance.name, userType='normal', userKey=core.generate_user_key(),
            quota=size)
    elif user['userQuota'] != size:
        sx.modifyUser(instance.name, quota=size)


@receiver(pre_delete, sender=Cluster)
def remove_user(instance, **kwargs):
    """Remove the user along with the cluster."""
    if not instance.is_root:
        try:
            sx.removeUser(instance.name)
        except SXClusterNotFound:
            pass  # This user didn't exist in the first place


class ClusterExpiration(models.Model):
    """Handles the info about cluster expiration."""
    cluster = models.OneToOneField(Cluster, verbose_name=_("Cluster"),
                                   related_name='_expiration')
    expiration_date = models.DateField(verbose_name=_("Expiration date"))

    user_permissions = JSONField(default={})
    """Copy of user permissions on expiration date."""

    def expire(self):
        """Collect, then disable existing users permissions."""
        success = True
        user_permissions = {}
        for v in self.cluster.volumes:  # v is a volume object
            perms = {'grant-read': [], 'grant-write': [], 'grant-manager': []}
            user_permissions[v.full_name] = perms
            for u in v.acl:  # u is a dictionary of one user's permissions
                if not u['is_reserved']:
                    for perm in 'read', 'write', 'manager':
                        if u[perm]:
                            perms['grant-' + perm].append(u['email'])
            try:
                sx.updateVolumeACL(v.full_name, {
                    key.replace('grant', 'revoke'): value
                    for key, value in perms.iteritems()})
            except SXClientException as e:
                success = False
                msg = '\n'.join([
                    "Failed to revoke permissions on an expired cluster.",
                    "\tCluster:\t{}".format(self.cluster.name),
                    "\tVolume:\t{}".format(v.full_name),
                    "\tException:\t{}".format(e),
                ])
                logger.error(msg)
        if success:
            self.user_permissions = user_permissions
            self.save()

    def restore(self, delete=True):
        """Restore saved permissions."""
        success = True
        for volume, perms in self.user_permissions.iteritems():
            try:
                sx.updateVolumeACL(volume, perms)
            except SXClientException as e:
                success = False
                msg = '\n'.join([
                    "Failed to restore some permisisons.",
                    "\tCluster:\t{}".format(self.cluster.name),
                    "\tVolume:\t{}".format(volume.full_name),
                    "\tPermissions:\n{}".format(pprint.pformat(perms)),
                    "\tException:\t{}".format(e),
                ])
                logger.error(msg)
        if success:
            if delete:
                self.expiration_date = None
                self.delete()
            else:
                self.user_permissions = {}
                self.save()


class AccessLogEntryOperation(DjangoChoices):
    LIST = ChoiceItem('LIST', _("List"))
    DOWNLOAD = ChoiceItem('DOWNLOAD', _("Download"))
    UPLOAD = ChoiceItem('UPLOAD', _("Upload"))
    DELETE = ChoiceItem('DELETE', _("Delete"))


class AccessLogEntryModel(models.Model):

    OPERATIONS = AccessLogEntryOperation
    task_id = models.UUIDField(db_index=True)

    datetime = models.DateTimeField(db_index=True)
    volume = models.TextField()
    path = models.TextField()
    operation = ChoiceField(choices=OPERATIONS)
    user = models.TextField()
    ip = models.TextField()
    user_agent = models.TextField()

    class Meta:
        ordering = ['datetime']
        index_together = ['task_id', 'datetime']

    @property
    def full_path(self):
        volume = self.volume.rstrip('/')
        path = self.path.lstrip('/')
        return '{}/{}'.format(volume, path)
