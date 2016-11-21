# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.utils.translation import ugettext_lazy as _


def validate_email(cluster, email):
    email = email.lower()
    if any(email == u.email.lower() for u in cluster.users):
        return False, _(
            "User with this e-mail address already exists in this cluster.")
    return True, None
