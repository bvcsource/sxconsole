# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djchoices import DjangoChoices, ChoiceItem

from sxconsole.utils.fields import ChoiceField
from sxconsole.utils.mail import send_mail
from sxconsole.utils.models import TokenModel
from .managers import AdminManager


console_app_name = settings.SKIN['console_app_name']


class AdminLevels(DjangoChoices):
    """Choices for Admin level."""
    ADMIN = ChoiceItem('ADMIN', _("Admin"))
    SUPER_ADMIN = ChoiceItem('SUPER_ADMIN', _("Super Admin"))
    ROOT_ADMIN = ChoiceItem('ROOT_ADMIN', _("Root Admin"))


class Admin(AbstractBaseUser):
    """An user of the console. Only admins have access to the console."""
    LEVELS = AdminLevels
    USERNAME_FIELD = 'email'

    email = models.EmailField(verbose_name=_("Email"), unique=True)
    level = ChoiceField(verbose_name=_("Level"), choices=LEVELS,
                        default=LEVELS.ADMIN)

    objects = AdminManager()

    class Meta:
        ordering = ('-level', 'email')

    @classmethod
    def get_or_invite(cls, email):
        admin, created = cls.objects.get_or_create(email=email)
        if created:
            PasswordReset.objects.create(admin=admin).send_invitation()
        return admin, created

    @property
    def clusters(self):
        """Superadmin can manage all clusters."""
        if self.is_superadmin:
            from sxconsole.clusters.models import Cluster
            return Cluster.objects
        return self._clusters

    @property
    def is_superadmin(self):
        return self.level in (self.LEVELS.SUPER_ADMIN, self.LEVELS.ROOT_ADMIN)

    @property
    def is_root_admin(self):
        return self.level == self.LEVELS.ROOT_ADMIN


class PasswordReset(TokenModel):
    """Token for resetting passwords."""
    admin = models.ForeignKey(Admin)

    def consume(self, password):
        """Set the password and remove the token."""
        if not settings.DEMO:
            self.admin.set_password(password)
            self.admin.save()
        PasswordReset.objects.filter(admin=self.admin).delete()

    def send_reset(self):
        """Send an email with the password reset link."""
        subject = _("{app_name} password reset") \
            .format(app_name=console_app_name)
        tpl = 'mail/password_reset.html'
        url_name = 'password_reset'

        ctx = {
            'app_name': console_app_name,
            'link': reverse(url_name, args=[self.token]),
        }
        return send_mail(subject, self.admin.email, tpl, ctx)

    def send_invitation(self):
        """Send an email with the invitation."""
        subject = _("Welcome to {app_name}!") \
            .format(app_name=console_app_name)
        tpl = 'mail/invite.html'
        url_name = 'invitation'

        ctx = {
            'app_name': console_app_name,
            'link': reverse(url_name, args=[self.token]),
        }
        return send_mail(subject, self.admin.email, tpl, ctx)
