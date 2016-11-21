# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

from __future__ import absolute_import, unicode_literals

import os
from logging import Formatter
from subprocess import check_output, CalledProcessError


def configure_logging(LOGS_DIR):

    if not os.path.isdir(LOGS_DIR):
        print('Creating logs directory ({})'.format(LOGS_DIR))
        os.makedirs(LOGS_DIR)

    def file_handler(filename, **kwargs):
        kwargs.setdefault('level', 'WARNING')
        handler = {
            'formatter': 'file',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, filename),
            'when': 'midnight',
            'backupCount': 10,
        }
        handler.update(kwargs)
        return handler

    date_format = '%H:%M:%S'
    minimal_format = '[%(asctime)s] %(message)s'
    console_format = '[%(asctime)s %(name)s] %(message)s'
    file_format = '[%(asctime)s %(name)s %(levelname)s] %(message)s'

    LOGGING = {
        'version': 1,
        'loggers': {
            'django.db': {
                'handlers': ['console_db'],
                'level': 'DEBUG',
                'propagate': False,
            },
            'django': {
                'handlers': ['console_server', 'django_file', 'mail_admins'],
                'level': 'INFO',
            },
            'rq.worker': {
                'handlers': ['console', 'rq_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'sxconsole': {
                'handlers': ['console', 'sxconsole_file'],
                'level': 'DEBUG',
            },
        },

        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True,
            },
            'console_db': {
                'level': 'DEBUG',
                'formatter': 'db',
                'class': 'logging.StreamHandler',
            },
            'console_server': {
                'level': 'DEBUG',
                'formatter': 'server',
                'class': 'logging.StreamHandler',
            },
            'console': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.StreamHandler',
            },
            'django_file': file_handler('django.log'),
            'rq_file': file_handler('rq.log'),
            'sxconsole_file': file_handler('sxconsole.log'),
        },

        'formatters': {
            'default': {
                '()': ColoredFormatter,
                'format': console_format,
                'datefmt': date_format,
            },
            'db': {
                '()': DbFormatter,
                'format': minimal_format,
                'datefmt': date_format,
            },
            'server': {
                '()': ServerFormatter,
                'format': minimal_format,
                'datefmt': date_format,
            },
            'file': {
                'format': file_format,
            },
        },
    }
    return LOGGING


class ColoredFormatter(Formatter):

    COLORS = {
        'DEBUG': '\033[38;5;8m',
        'INFO': '\033[38;5;4m',
        'WARNING': '\033[38;5;3m',
        'ERROR': '\033[38;5;5;1m',
        'CRITICAL': '\033[38;5;1;1m',
    }
    RESET = '\033[0m'

    def format(self, record):
        message = super(ColoredFormatter, self).format(record)
        level = record.levelname
        if level in self.COLORS:
            message = '{}{}{}'.format(
                self.COLORS[level], message, self.RESET)
        return message


class ServerFormatter(ColoredFormatter):

    COLORS = ColoredFormatter.COLORS.copy()
    COLORS.pop('INFO')

    def format(self, record):
        message = super(ServerFormatter, self).format(record)
        if record.levelname == 'INFO' and \
                message.endswith(' 0') and \
                '"GET /' in message:
            message = '{}{}{}'.format(
                self.COLORS['DEBUG'], message, self.RESET)
        return message


class DbFormatter(ColoredFormatter):

    def __init__(self, *args, **kwargs):
        super(DbFormatter, self).__init__(*args, **kwargs)

        try:
            max_length = check_output(['tput', 'cols'])
            max_length = int(max_length)
        except (CalledProcessError, ValueError):
            max_length = None
        self.max_length = max_length

    def format(self, record):
        """Make sure that at most only one line is displayed."""
        start_color = self.COLORS[record.levelname]
        end_color = self.RESET

        message = super(DbFormatter, self).format(record)
        message = ' '.join(message.split())
        message = message[len(start_color):-len(end_color)]

        if self.max_length is not None and len(message) > self.max_length:
            message = message[:self.max_length - 1] + '\u2026'
        return '{}{}{}'.format(start_color, message, end_color)
