# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from django.core.management.base import BaseCommand, CommandError

from sxconsole.accounts.models import Admin


class Command(BaseCommand):
    help = 'Deletes a Root Admin user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        password = kwargs['password']
        try:
            admin = Admin.objects.get(
                level=Admin.LEVELS.ROOT_ADMIN,
                email=email,
            )
        except Admin.DoesNotExist:
            raise CommandError('No such root admin: {}'.format(email))

        if admin.check_password(password):
            admin.delete()
            self.stdout.write('Root admin {} deleted.'.format(email))
        else:
            raise CommandError('Invalid password.')
