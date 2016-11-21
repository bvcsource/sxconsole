# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

import re
from logging import getLogger
from socket import error as SocketError
from urlparse import urljoin

from django.conf import settings
from django.core.mail import send_mail as dj_send_mail
from django.template.loader import render_to_string


logger = getLogger(__name__)


def send_mail(subject, to, template=None, context=None, content=None):
    """Useful wrapper around django's send_mail."""

    if isinstance(to, basestring):
        to = [to]  # send_mail expects a list of recipients

    if not content:
        if 'link' in context:
            context['link'] = urljoin(settings.APP_URL, context['link'])
        content = render_to_string(template, context)
    content = content.strip()
    content = re.sub('\n\n+', '\n\n', content)

    from_ = settings.DEFAULT_FROM_EMAIL

    try:
        dj_send_mail(subject, content, from_, to)
        return True
    except SocketError as e:
        logger.error("Failed to send e-mail: {}".format(e))
        return False
