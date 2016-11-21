# Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
# License: GPLv2 or later, see LICENSE for more details.

'''
'''

from csv import DictWriter
from io import BytesIO


OUTPUT_CSV_FIELDS = (
    'datetime', 'volume', 'path', 'operation', 'user', 'ip', 'user_agent')


def access_log_to_csv(access_log):
    output = BytesIO()
    writer = DictWriter(output, OUTPUT_CSV_FIELDS)
    writer.writeheader()
    for entry in access_log:
        data = serialize_entry(entry)
        writer.writerow(data)
    output.seek(0)
    return output


def serialize_entry(entry):
    serialized = {
        'datetime': entry.datetime.isoformat(sep=' '),
        'ip': entry.ip,
        'operation': entry.get_operation_display(),
        'path': entry.path,
        'user': entry.user,
        'user_agent': entry.user_agent,
        'volume': entry.volume,
    }
    return serialized
