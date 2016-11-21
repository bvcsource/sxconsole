#!/usr/bin/env python

# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

import re
import sys
from subprocess import check_call, check_output


VERSION_FILE = 'sxconsole/__init__.py'


def main(input):
    if not is_repo_clean():
        print 'You have some uncommitted changes! Aborting...'
        sys.exit(1)

    try:
        version = parse_version(input)
    except ValueError:
        show_help()
        sys.exit(1)
    pretty_version = version_to_string(version)

    # Set the new version
    set_version(version)
    commit_version(pretty_version)
    create_tag(pretty_version)

    # Set a development version
    set_version(version + ["'dev'"])
    commit_version('Back to development')

    if not user_confirms_changes():
        print 'Reverting changes...'
        undo_changes(tag=pretty_version)
        sys.exit(1)
    push_changes()


def is_repo_clean():
    return check_output(['git', 'diff']) == '' and \
        check_output(['git', 'diff', '--cached']) == ''


def parse_version(input):
    input = re.split('\D', input)
    input = filter(bool, input)  # Remove empty strings
    version = map(int, input)
    if len(version) < 3:
        raise ValueError()
    return version


def show_help():
    print '''
Usage: ./new_version.py VERSION
Set new app version, tag it and push it.
Example: ./new_version.py v1.2.3
'''.strip()


def version_to_string(version):
    dot_separated_version = '.'.join(str(v) for v in version)
    return 'v' + dot_separated_version


def set_version(version):
    with open(VERSION_FILE) as f:
        file_contents = f.read()

    comma_separated_version = ', '.join(str(v) for v in version)
    new_file_contents = re.sub(
        r'^VERSION = .*$',
        'VERSION = ({})'.format(comma_separated_version),
        file_contents,
        count=1,
        flags=re.MULTILINE,
    )

    with open(VERSION_FILE, 'w') as f:
        f.write(new_file_contents)


def commit_version(message):
    check_call(['git', 'add', VERSION_FILE])
    check_call(['git', 'commit', '-m', message])


def create_tag(tag):
    check_call(['git', 'tag', tag])


def user_confirms_changes():
    print
    check_call(['git', 'show', '-U0', '--oneline', 'HEAD~1'])
    print
    check_call(['git', 'show', '-U0', '--oneline', 'HEAD~0'])
    print
    answer = raw_input('Is this ok? (Y/n) ')
    return not answer.strip().lower().startswith('n')


def undo_changes(tag):
    check_call(['git', 'tag', '--delete', tag])
    check_call(['git', 'reset', '--hard', 'HEAD~2'])


def push_changes():
    check_call(['flake8', VERSION_FILE])  # Sanity check
    check_call(['git', 'push'])
    check_call(['git', 'push', '--tags'])


if __name__ == '__main__':
    main(sys.argv[1])
