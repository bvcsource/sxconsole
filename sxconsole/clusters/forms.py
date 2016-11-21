# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import json

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from sizefield.widgets import FileSizeWidget

from sxconsole import core
from sxconsole.utils.forms import TwbsForm, EmailField
from . import models


def date_widget(config=None):
    attrs = {'class': 'js-datepicker'}
    if config:
        data_conf = json.dumps(config)
        attrs['data-config'] = data_conf
    return forms.DateInput(attrs=attrs, format='%Y-%m-%d')


class ClusterForm(TwbsForm, forms.ModelForm):
    """Form for Clusters."""

    expiration_date = forms.DateField(
        label=_("Expiration date"),
        help_text=_(
            "Optional. If set, the cluster will become unusable "
            "on this date."),
        widget=date_widget({'startDate': '0d'}),
        required=False)

    class Meta:
        model = models.Cluster
        fields = ('max_volumes', 'max_users', 'size', 'thin_provisioning',
                  'replicas', 'expiration_date')

    def __init__(self, *args, **kwargs):
        super(ClusterForm, self).__init__(*args, **kwargs)
        size_validators = self._meta.model._meta.get_field('size').validators
        self.fields['size'].validators.extend(size_validators)

    def clean_expiration_date(self):
        date = self.cleaned_data.get('expiration_date')
        if not date:
            return

        # Compare given date against current date:
        current = timezone.now()
        if timezone.is_aware(current):
            current = timezone.localtime(current)
        current = current.date()
        if date < current:
            raise ValidationError(_("You can't set a date in the past."))
        return date

    def save(self, commit=True):
        self.instance = super(ClusterForm, self).save(commit=False)
        if commit:
            self.instance.save()
            # Manage the ClusterExpiration object
            expiration_date = self.cleaned_data['expiration_date']
            update_cluster_expiration_date(self.instance, expiration_date)
        return self.instance


def update_cluster_expiration_date(cluster, expiration_date):
    if expiration_date:
        models.ClusterExpiration.objects.update_or_create(
            cluster=cluster,
            defaults={'expiration_date': expiration_date},
        )
    elif cluster.expiration is not None:
        cluster.expiration.restore()


class CreateClusterForm(ClusterForm):
    """Handles the creation of Cluster and its admin."""

    email = EmailField(
        label=_("Cluster admin"),
        help_text=_("E-mail address of the cluster's admin."), required=False)

    class Meta(ClusterForm.Meta):
        fields = ('name', 'email') + ClusterForm.Meta.fields


class LogsFiltersForm(TwbsForm, forms.Form):
    from_date = forms.DateField(label=_("From"), widget=date_widget())
    till_date = forms.DateField(label=_("Until"), widget=date_widget())
    user_filter = forms.CharField(label=_("User"), required=False)
    volume_filter = forms.CharField(label=_("Volume"), required=False)


class S3ImportForm(TwbsForm, forms.Form):
    s3_host = forms.CharField(label=_("S3 host"))
    s3_port = forms.IntegerField(
        required=False, label=_("S3 port"), validators=[core.port_validator],
        help_text=_(
            "Custom port number used to connect to the S3 host. Default is "
            "443."))
    s3_key_id = forms.CharField(label=_("S3 access key ID"))
    s3_secret_key = forms.CharField(label=_("S3 secret access key"))
    default_size = forms.IntegerField(
        required=False, label=_("Default new volume size"),
        widget=FileSizeWidget(), validators=[core.size_validator],
        help_text=_(
            "If destination volume for any given bucket doesn't exist, it "
            "will be created with the size given here. If no value is given, "
            "the size will be slightly larger than the size of the bucket. "
            "Suffixes can be used, e.g. 100GB."))
    replicas = forms.IntegerField(
        label=_("Default new volume replicas"), initial=2,
        validators=[core.replicas_validator], help_text=_(
            "If destination volume for any given bucket doesn't exist, it "
            "will be created with the replica count given here."))
    s3_validate_certs = forms.BooleanField(
        required=False, label=_("Validate S3 SSL certificates"), initial=True)
    advanced = forms.BooleanField(
        required=False, label=_("Advanced"))

    def __init__(self, *args, **kwargs):
        self.cluster = kwargs.pop('cluster')
        super(S3ImportForm, self).__init__(*args, **kwargs)
        replicas = self.cluster.replicas
        if replicas:
            field = self.fields['replicas']
            field.widget.attrs['readonly'] = True
            field.initial = replicas
