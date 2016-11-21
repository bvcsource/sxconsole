# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''


def selective_update(target, source, keys):
    """
    Update a `target` with given `keys` from `source`

    >>> target = {'a': 'a'}
    >>> source = {'b': 'b', 'c': 'c'}
    >>> selective_update(target, source, ['b'])
    >>> target.keys()
    ['a', 'b']
    """
    selected = dict_slice(source, keys)
    target.update(selected)


def dict_slice(d, keys):
    """
    Create new dict by picking `keys` from `d`.

    >>> d = {'a': 'a', 'b': 'b', 'c': 'c'}
    >>> dict_slice(d, ['a', 'b'])
    {'a': 'a', 'b': 'b'}
    """
    return {k: d[k] for k in keys}
