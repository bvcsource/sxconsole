# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django import forms
from django.utils.translation import ugettext_lazy as _
from sizefield.widgets import FileSizeWidget

from sxconsole import core
from sxconsole.entities import IndexingModes
from sxconsole.sx_api import sx
from sxconsole.utils.forms import TwbsForm
from .validators import validate_volume_size, validate_name


class BaseVolumeForm(TwbsForm, forms.Form):
    name = forms.CharField(label=_("Name"), max_length=50,
                           validators=[core.identifier_validator])
    size = forms.IntegerField(
        label=_("Size"), widget=FileSizeWidget(),
        validators=[core.size_validator])
    revisions = forms.IntegerField(
        label=_("Revisions"), validators=[core.revisions_validator], initial=1)
    replicas = forms.IntegerField(label=_("Replicas"),
                                  validators=[core.replicas_validator])
    indexing = forms.ChoiceField(label=_("Indexing"))

    def __init__(self, *args, **kwargs):
        self.cluster = kwargs.pop('cluster')
        self.current_size = kwargs.pop('current_size', 0)
        super(BaseVolumeForm, self).__init__(*args, **kwargs)
        self.setup_replicas_field()
        self.setup_indexing_field()

    def setup_replicas_field(self):
        field = self.fields['replicas']
        fixed_replicas = self.cluster.replicas
        if fixed_replicas:
            field.initial = fixed_replicas
            field.widget.attrs['readonly'] = True
        else:
            max_replicas = len(sx.listNodes()['nodeList'])
            field.min_value = 1
            field.max_value = max_replicas
            field.initial = min(max_replicas, 2)
            field.widget.attrs['min'] = field.min_value
            field.widget.attrs['max'] = field.max_value

    def setup_indexing_field(self):
        if sx.has_indexer:
            self.fields['indexing'].choices = IndexingModes.choices
        else:
            self.fields.pop('indexing')

    def clean_size(self):
        size = self.cleaned_data['size']
        valid, msg = validate_volume_size(
            self.cluster, size, self.current_size)
        if valid:
            return size
        else:
            raise forms.ValidationError(msg)

    def clean_indexing(self):
        value = self.cleaned_data['indexing']
        if value not in IndexingModes.values:
            raise forms.ValidationError(_("Enter a valid value"))
        return value

    def clean_replicas(self):
        if self.cluster.replicas:
            return self.cluster.replicas
        return self.cleaned_data['replicas']

    def clean_name(self):
        name = self.cleaned_data['name'].lower()
        valid, msg = validate_name(self.cluster, name)
        if valid:
            return name
        else:
            raise forms.ValidationError(msg)


class NewVolumeForm(BaseVolumeForm):
    encryption = forms.BooleanField(
        required=False, label=_("Encryption"), help_text=_(
            "Important: only users with Manager permission can initialize "
            "an encrypted volume.\n"
            "The user will be prompted to set a password on first upload."))

    def __init__(self, *args, **kwargs):
        super(NewVolumeForm, self).__init__(*args, **kwargs)

        if not sx.has_encryption:
            self.fields.pop('encryption')


class UpdateVolumeForm(BaseVolumeForm):

    def __init__(self, *args, **kwargs):
        super(UpdateVolumeForm, self).__init__(*args, **kwargs)

        if not sx.has_volume_rename:
            self.fields.pop('name')
        if not sx.has_volume_replica_change:
            self.fields.pop('replicas')

    def clean_name(self):
        new_name = self.cleaned_data['name']
        if new_name != self.initial['name']:
            return super(UpdateVolumeForm, self).clean_name()
        return new_name


class DeleteVolumeForm(TwbsForm, forms.Form):
    """Form for deleting a volume."""
    name = forms.CharField(label=_("Name"), max_length=50)

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        self.force = kwargs.pop('force')
        super(DeleteVolumeForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = self.force

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.force and name != self.name:
            raise forms.ValidationError(_("You entered a wrong name!"))
