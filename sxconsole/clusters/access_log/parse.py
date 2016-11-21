# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from csv import DictReader
from hashlib import sha1

from dateutil.parser import parse as dateutil_parse
from sxclient import UserData
from sxclient.exceptions import InvalidUserKeyError

from sxconsole.sx_api import sx


CSV_FIELDS = (
    'datetime', 'volume', 'path', 'operation', 'user', 'ip', 'user_agent')
STORAGE_VOLUME = 'sxmonitor'
STORAGE_DIR = 'access_logs'


class UserIDs:
    """Class for converting user ids to usernames."""

    def __init__(self):
        self.data = {}  # userID (sha1) -> username

    def update(self):
        for username in sx.listUsers():
            uid = sha1(username.encode('utf-8')).digest()
            self.data[uid] = username

    def get_username(self, hash):
        """Given a base64-encoded key, return the username."""
        try:
            uid = UserData.from_key(hash).uid
        except InvalidUserKeyError:
            uid = None
        return self.data.get(uid)

user_ids = UserIDs()


def parse_logfile_contents(contents):
    """Convert access log entry into a LogEntry object."""
    rows = DictReader(contents.splitlines(), CSV_FIELDS)
    for row in rows:
        yield parse_entry(row)


def parse_entry(entry):
    entry['datetime'] = dateutil_parse(entry['datetime'])
    entry['operation'] = entry['operation'].upper()

    token = entry['user']
    entry['user'] = user_ids.get_username(token) or token
    return entry
