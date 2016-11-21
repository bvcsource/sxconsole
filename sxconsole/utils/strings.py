# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''
import hashlib
import string

from unidecode import unidecode

valid_identifier_chars = string.letters + string.digits + '-_'


def get_volume_naming_function(token_separator='-'):
    def join_args(*args):
        return token_separator.join(filter(None, args))

    volumes = set()

    def get_volume_name(oldname):
        name = asciify(oldname)
        token = ''
        if (join_args(name, token) in volumes or
                len(join_args(name, token)) < 2):
            token = hashlib.md5(oldname).hexdigest()
        name = join_args(name, token)
        volumes.add(name)
        return name
    return get_volume_name


def asciify(s):
    s = unidecode(s)
    result_list = []
    for char in s:
        if char in valid_identifier_chars:
            result_list.append(char)
    result = ''.join(result_list).lower()
    return result
