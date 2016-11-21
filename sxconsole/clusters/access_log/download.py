# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from itertools import chain
from logging import getLogger

from sxconsole import core
from sxconsole.sx_api import sx
from .parse import parse_logfile_contents
from .utils import ensure_sxmonitor


logger = getLogger(__name__)
STORAGE_VOLUME = 'sxmonitor'
STORAGE_DIR = 'access_logs'


def download_logs_for_range(from_, till):
    futures = []
    with ThreadPoolExecutor(max_workers=1) as e:
        # results = e.map(download_logs_for_date, date_range(from_, till))
        for date in date_range(from_, till):
            future = e.submit(download_logs_for_date, date)
            futures.append(future)
    results = (f.result() for f in futures)
    return chain.from_iterable(results)


def download_logs_for_date(date):
    ensure_sxmonitor()  # Run this before starting thread executor

    path = build_access_log_path(date)
    files = sx.listFiles(core.log_volname, path)['fileList']
    print 'Found {} files for {}'.format(len(files), date)

    futures = []
    with ThreadPoolExecutor(max_workers=1) as e:
        for filename in files:
            future = e.submit(download_logs_from_filename, filename)
            futures.append(future)
    results = (f.result() for f in futures)
    return chain.from_iterable(results)


def download_logs_from_filename(filename):
    filename = filename.lstrip('/')
    log_content = sx.downloader.get_file_content(core.log_volname, filename)
    logger.info("Parsing {}...".format(filename))

    results = parse_logfile_contents(log_content)
    return results


def build_access_log_path(date):
    """Return sxmonitor path for access logs on a given date.

    >>> from datetime import datetime
    >>> build_access_log_path(datetime(2016, 5, 4, 15, 56))
    'access_logs/2016-05-04.*.csv'
    """
    path = '{}/{}.*.csv'.format(STORAGE_DIR, date.strftime('%Y-%m-%d'))
    return path


def date_range(from_, till):
    """Return a list of dates in a closed [from_, till] range.

    >>> from datetime import datetime
    >>> dates = date_range(datetime(2016, 5, 1), datetime(2016, 5, 3))
    >>> [d.strftime('%Y-%m-%d') for d in dates]
    ['2016-05-01', '2016-05-02', '2016-05-03']
    """
    num_days = (till - from_).days + 1  # Adjust for closed range
    dates = [from_ + timedelta(days=i) for i in range(num_days)]
    return dates
