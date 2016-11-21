# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.conf import settings

from sxconsole import get_version
from sxconsole.s3_api import s3
from sxconsole.sx_api import sx


def sx_console(request):
    context = {
        'BASE_TEMPLATE': 'base.html' if request.user.is_authenticated()
        else 'public_base.html',
        'VERSION': get_version(),
        'HAS_INDEXER': lambda: sx.has_indexer,
        'HAS_LIBRES3': lambda: s3.is_available,
        'SKIN': settings.SKIN,
        'DEMO': settings.DEMO,
        'DISABLE_SX_MANAGEMENT': settings.APP_CONF.get(
            'disable_sx_management'),
    }
    if request.user.is_authenticated():
        clusters = sorted(request.user.clusters.all(),
                          key=lambda c: (c.is_root, c.name))
        context['side_panel'] = {
            'clusters': clusters,
            'clusters_count': sum(not c.is_root for c in clusters),
        }
    return context
