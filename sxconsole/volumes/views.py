# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import json
from urllib import urlencode

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from sxclient.exceptions import SXClientException

from sxconsole import core
from sxconsole.sx_api import sx
from sxconsole.utils.clusters import create_volume, get_free_size
from sxconsole.utils.views import ClusterViewMixin, VolumeViewMixin
from sxconsole.utils.volumes import update_volume, make_public, make_private
from . import forms, tasks
from .validators import can_add_volume


class CreateVolumeView(ClusterViewMixin, generic.FormView):
    """Adds a volume to the cluster."""
    form_class = forms.NewVolumeForm
    template_name = 'volumes/add_volume.html'
    url_name = 'add_volume'
    title = _("Adding a new volume")

    def dispatch(self, *args, **kwargs):
        """Check if it's possible to add a volume."""
        cluster = self.object
        can, msg = can_add_volume(cluster, self.request.user)
        if not can:
            messages.error(self.request, msg)
            return redirect(cluster)
        return super(CreateVolumeView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CreateVolumeView, self).get_form_kwargs()
        kwargs['cluster'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super(CreateVolumeView, self).get_context_data(**kwargs)
        size_init = {
            'minValue': core._min_volume_size,
            'maxValue': get_free_size(self.object),
        }
        try:
            size_init['value'] = ctx['form'].cleaned_data['size']
        except (AttributeError, KeyError):
            pass
        ctx['size_init'] = json.dumps(size_init)
        return ctx

    def form_valid(self, form):
        try:
            create_volume(self.object, **form.cleaned_data)
        except SXClientException as e:
            form.add_error(None, core.get_exception_msg(e))
            return self.form_invalid(form)
        return redirect(self.object)


class VolumeAclView(VolumeViewMixin, generic.TemplateView):
    template_name = 'volumes/volume_acl.html'
    url_name = 'volume_acl'

    @property
    def title(self):
        return self.volume.name

    def get_context_data(self, **kwargs):
        add_user_url = reverse('add_user', args=[self.object.pk])
        add_user_url += '?' + urlencode({'next': self.redirect_to_volume.url})
        acl_init = json.dumps({
            'clusterId': self.object.pk,
            'volumeName': self.volume.name,
        })
        return super(VolumeAclView, self).get_context_data(
            add_user_url=add_user_url, acl_init=acl_init, **kwargs)


class UpdateVolumeView(VolumeViewMixin, generic.FormView):
    template_name = 'volumes/edit_volume.html'
    form_class = forms.UpdateVolumeForm
    url_name = 'edit_volume'

    @property
    def title(self):
        return _("Updating {}").format(self.volume.name)

    def dispatch(self, *args, **kwargs):
        if self.object.is_expired and not self.request.user.is_superadmin:
            messages.error(self.request, _(
                "You can't edit this volume because its cluster has expired."))
            return redirect(self.object)
        return super(UpdateVolumeView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(UpdateVolumeView, self).get_form_kwargs()
        kwargs['cluster'] = self.object
        kwargs['current_size'] = self.volume.size
        return kwargs

    def get_initial(self):
        return {
            'name': self.volume.name,
            'size': self.volume.size,
            'revisions': self.volume.revisions,
            'replicas': self.volume.replicas,
            'indexing': self.volume.indexing,
        }

    def get_context_data(self, **kwargs):
        ctx = super(UpdateVolumeView, self).get_context_data(**kwargs)
        try:
            value = ctx['form'].cleaned_data['size']
        except (AttributeError, KeyError):
            value = self.volume.size
        size_init = {
            'minValue': core._min_volume_size,
            'maxValue': get_free_size(self.object, volume=self.volume),
            'value': value,
        }
        ctx['size_init'] = json.dumps(size_init)
        return ctx

    def form_valid(self, form):
        try:
            update_volume(self.volume, form.cleaned_data)
        except SXClientException as e:
            form.add_error(None, core.get_exception_msg(e))
            return self.form_invalid(form)
        return redirect(self.object)


class DeleteVolumeView(VolumeViewMixin, generic.FormView):
    template_name = 'volumes/delete_volume.html'
    form_class = forms.DeleteVolumeForm
    url_name = 'delete_volume'

    @property
    def title(self):
        return _("Deleting {}").format(self.volume.name)

    def get_form_kwargs(self):
        kwargs = super(DeleteVolumeView, self).get_form_kwargs()
        kwargs['name'] = self.volume.name
        kwargs['force'] = not self.volume.empty
        return kwargs

    def form_valid(self, form):
        if form.force:
            self.force_delete_volume()
        else:
            self.delete_volume()
        return redirect(self.object)

    def delete_volume(self):
        try:
            sx.deleteVolume(self.volume.full_name)
            messages.success(self.request, _(
                "The volume has been removed."))
        except SXClientException as e:
            messages.error(self.request, core.get_exception_msg(e))

    def force_delete_volume(self):
        tasks.delete_volume(self.request.user, self.volume.full_name)
        messages.info(self.request, _(
            "The volume has been marked for deletion "
            "and will be removed soon."))


class MakeVolumePublic(VolumeViewMixin, generic.View):
    url_name = 'make_volume_public'

    def post(self, *args, **kwargs):
        make_public(self.volume.full_name)
        messages.info(self.request, _(
            "Volume {} is now public")
            .format(self.volume.name))
        return self.redirect_to_volume


class MakeVolumePrivate(VolumeViewMixin, generic.View):
    url_name = 'make_volume_private'

    def post(self, *args, **kwargs):
        make_private(self.volume.full_name)
        messages.info(self.request, _(
            "Volume {} is now private")
            .format(self.volume.name))
        return self.redirect_to_volume
