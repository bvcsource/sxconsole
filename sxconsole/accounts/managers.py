# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from django.contrib.auth.models import BaseUserManager


class AdminManager(BaseUserManager):

    def visible_to(self, user):
        """Select user's co-admins."""
        if user.is_superadmin:
            return self.all()
        return self.filter(_clusters__admins=user).distinct()
