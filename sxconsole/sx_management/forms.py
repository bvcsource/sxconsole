# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django import forms
from django.utils.translation import ugettext_lazy as _
from sizefield.utils import filesizeformat
from sizefield.widgets import FileSizeWidget

from sxconsole.utils.forms import FieldsetMixin, TwbsForm


class ClusterManagementForm(FieldsetMixin, TwbsForm, forms.Form):
    sxweb_address = forms.URLField(label=_("SXWeb address"), required=False)
    sxshare_address = forms.URLField(label=_("SXShare address"),
                                     required=False)
    libres3_address = forms.URLField(label=_("LibreS3 address"),
                                     required=False)
    cluster_size = forms.IntegerField(
        label=_("Cluster size"),
        widget=FileSizeWidget(),
    )

    hb_keepalive = forms.IntegerField(label=_("Keepalive"))
    hb_warntime = forms.IntegerField(label=_("Warn time"))
    hb_deadtime = forms.IntegerField(label=_("Dead time"))
    hb_initdead = forms.IntegerField(label=_("Init dead"))

    fieldsets = (
        (None, ('cluster_size',)),
        (_("SX Enterprise configuration"), (
            'sxweb_address', 'sxshare_address', 'libres3_address')),
        (_("Raft settings"), (
            'hb_keepalive', 'hb_warntime', 'hb_deadtime', 'hb_initdead')),
    )

    def clean_sxweb_address(self):
        return self._clean_url('sxweb_address')

    def clean_sxshare_address(self):
        return self._clean_url('sxshare_address')

    def clean_libres3_address(self):
        return self._clean_url('libres3_address')

    def clean_cluster_size(self):
        size = self.initial['cluster_size']
        target = self.cleaned_data['cluster_size']

        if not target:
            return size

        # Since this field is handled by FileSizeWidget, it may report slightly
        # different values from the actual ones. (1040GB -> 1.0TB -> 1024GB)
        # Therefore, `target` is ignored if it did not change significantly.
        if abs(size - target) < 16 or \
                filesizeformat(size) == filesizeformat(target):
            return size

        return target

    def _clean_url(self, name):
        """Used to clean url for clusterMeta."""
        url = self.cleaned_data[name]
        if not url:
            return ''
        if not url.endswith('/'):
            url += '/'
        return url.encode('hex')
