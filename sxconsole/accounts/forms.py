# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm as DjAuthForm
from django.utils.translation import ugettext_lazy as _

from sxconsole.clusters.models import Cluster
from sxconsole.utils.forms import (
    TwbsForm, EmailField, NewPasswordForm, FieldOrderMixin, get_password_field,
)
from .models import Admin


class AuthenticationForm(TwbsForm, DjAuthForm):
    error_messages = DjAuthForm.error_messages.copy()
    error_messages['invalid_login'] = _(
        "Please enter a correct email and password. "
        "Note that both fields may be case-sensitive.")

    remember = forms.BooleanField(label=_("Remember me"), required=False)

    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        if settings.DEMO:
            self.fields['password'].widget.render_value = True
            self.initial.update({
                'username': settings.DEMO_USER,
                'password': settings.DEMO_PASS})


class EmailForm(TwbsForm, forms.Form):
    """Form for providing an email."""

    email = EmailField()


class AdminEmailForm(EmailForm):
    """Form for retrieving admins by email."""

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            admin = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            raise forms.ValidationError(
                _("There is no user with this e-mail address."))
        self.cleaned_data['admin'] = admin
        return email


class AdminForm(TwbsForm, forms.ModelForm):
    """Form for Admins."""

    email = EmailField()

    class Meta:
        model = Admin
        fields = ('level', 'email')

    def __init__(self, *args, **kwargs):
        self.admin = kwargs.pop('admin')
        super(AdminForm, self).__init__(*args, **kwargs)

        if self.admin.is_root_admin:
            self.fields['level'].choices = [
                (id, name) for id, name in Admin.LEVELS()
                if id != Admin.LEVELS.ROOT_ADMIN]
        else:
            self.fields.pop('level')


class ChangePasswordForm(FieldOrderMixin, NewPasswordForm):
    current_password = get_password_field(label=_("Current password"))

    field_order = ['current_password', 'password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        self.check_password = kwargs.pop('check_password')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        # Let's assume the user may have an invalid password (e.g. too short)
        self.fields['current_password'].validators = []
        self.fields['password'].label = _("New password")

    def clean_current_password(self):
        password = self.cleaned_data['current_password']
        if not self.check_password(password):
            raise forms.ValidationError(_("Please enter your password."))
        return password


class AddAdminClustersForm(forms.Form):
    """Form for adding some clusters to an admin."""
    clusters = forms.ModelMultipleChoiceField(queryset=Cluster.objects.none())

    def __init__(self, *args, **kwargs):
        """Store the queryset of allowed clusters."""
        qs = kwargs.pop('queryset')
        super(AddAdminClustersForm, self).__init__(*args, **kwargs)
        self.fields['clusters'].queryset = qs
