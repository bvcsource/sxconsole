# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from logging import getLogger

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from sxclient.exceptions import SXClientException

from sxconsole import core, msgs
from sxconsole.sx_api import sx
from sxconsole.utils.clusters import can_add_user
from sxconsole.utils.decorators import regular_user_only
from sxconsole.utils.users import add_user, remove_user, invite_user
from sxconsole.utils.views import (
    NewPasswordBase, ClusterViewMixin, UserViewMixin, RedirectMixin,
)
from . import forms
from .models import UserPasswordReset


logger = getLogger(__name__)
app_name = settings.SKIN['app_name']


class CreateUserView(RedirectMixin, ClusterViewMixin, generic.FormView):
    """Adds a user to the cluster."""
    form_class = forms.UserForm
    template_name = 'users/user_form.html'
    url_name = 'add_user'
    title = _("Adding a new user")

    def dispatch(self, *args, **kwargs):
        """Check if it's possible to add a user."""
        cluster = self.object
        can, msg = can_add_user(cluster, self.request.user)
        if not can:
            messages.error(self.request, msg)
            return redirect(cluster)
        return super(CreateUserView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateUserView, self).get_form_kwargs()
        kwargs['cluster'] = self.object
        return kwargs

    def get_initial(self):
        initial = super(CreateUserView, self).get_initial()
        initial.setdefault('message', self.object.get_setting(
            'invitation_message'))
        return initial

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            new_user_created = add_user(self.object, email=data['email'],
                                        password=data.get('password'))
        except SXClientException as e:
            form.add_error(None, core.get_exception_msg(e))
            return self.form_invalid(form)

        if new_user_created:
            if data['option'] == 'invite':
                self.send_invitation(data)
        else:
            messages.info(self.request, _(
                "This user already exists "
                "and has been added to this cluster."))
        return super(CreateUserView, self).form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def send_invitation(self, data):
        email = data['email']
        template = data['message']
        if data['save']:
            self.object.set_setting('invitation_message', template)

        sent = invite_user(
            email=email,
            template=template,
        )
        if sent:
            messages.success(self.request, _(
                "Invitation has been sent to {}").format(email))
        else:
            messages.error(self.request, msgs.failed_to_send_email)


@regular_user_only
class DeleteUserView(UserViewMixin, generic.TemplateView):
    template_name = 'users/delete_user.html'
    url_name = 'delete_user'

    @property
    def title(self):
        return _("Deleting {}").format(self.user.email)

    def post(self, *args, **kwargs):
        try:
            remove_user(self.user.email, self.object, self.object.is_root)
        except SXClientException as e:
            messages.error(self.request, core.get_exception_msg(e))
        return redirect(self.object)


@regular_user_only
class SendPasswordResetView(UserViewMixin, generic.TemplateView):
    template_name = 'users/confirm_send_password_reset.html'
    url_name = 'cluster_user_send_password_reset'
    title = _("Sending password reset")

    def dispatch(self, *args, **kwargs):
        if self.object.is_expired and not self.request.user.is_superadmin:
            messages.error(self.request, _(
                "You can't reset this user's password because its cluster "
                "has expired."))
            return redirect(self.object)
        elif not self.user.has_valid_email:
            messages.error(self.request, _(
                "You can't reset this user's password."))
            return redirect(self.object)
        return super(SendPasswordResetView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        msg = _("E-mail with password reset will be sent to {email}.").format(
            email=self.user.email)
        return super(SendPasswordResetView, self).get_context_data(
            confirmation_message=msg, **kwargs)

    def post(self, *args, **kwargs):
        sent = UserPasswordReset.objects.create(email=self.user.email) \
            .send_reset()
        if sent:
            messages.success(self.request, _(
                "Password reset sent to {}").format(self.user.email))
        else:
            messages.error(self.request, msgs.failed_to_send_email)
        return redirect(self.object)


class NewUserPasswordBase(NewPasswordBase):
    model = UserPasswordReset
    template_name = 'users/public_form.html'
    messages = False

    def token_invalid(self):
        return redirect(reverse(InvalidTokenView.url_name))

    def get_success_url(self):
        sxweb = sx.getClusterMetadata()['clusterMeta'].get('sxweb_address')
        if not sxweb:
            logger.warning(
                "SXWeb address is not set. User will be shown a generic "
                "success message.")
            return reverse(PasswordSetView.url_name)
        return sxweb.decode('hex')


class InvitationView(NewUserPasswordBase):
    url_name = 'cluster_user_invitation'
    title = _("Welcome")

    @property
    def help_text(self):
        return _(
            "Welcome to {app_name}! "
            "First, you have to set a password for your account.",
        ).format(app_name=app_name)


class PasswordResetView(NewUserPasswordBase):
    url_name = 'cluster_user_password_reset'
    title = _("Password reset")
    help_text = _("Enter a new password.")


class PasswordSetView(generic.TemplateView):
    """Displayed when a user's password has been set."""
    template_name = 'users/password_set.html'
    url_name = 'user_password_set'


class InvalidTokenView(generic.TemplateView):
    """Displayed when password reset token is invalid."""
    template_name = 'users/token_invalid.html'
    url_name = 'user_token_invalid'


@regular_user_only
class UserLoginOptionsView(UserViewMixin, generic.TemplateView):
    url_name = 'user_login_options'

    def get(self, request, *args, **kwargs):
        meta = sx.getClusterMetadata()['clusterMeta']
        libres3_address = meta.get('libres3_address', '').decode('hex')
        token = core.get_user_key(self.user.email)
        return JsonResponse({
            'libres3_address': libres3_address,
            'username': self.user.email,
            'token': token,
        })
