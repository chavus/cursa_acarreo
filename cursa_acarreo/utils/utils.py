from io import BytesIO, StringIO

import pytz
from csvalidate import ValidatedWriter
from flask import send_file


def nonify_dict(dict):
    for key in dict:
        if dict[key] == '':
            dict[key] = None
    return dict


def formatdate_mx(datetime_val):
    if datetime_val:
        timezone = pytz.timezone('America/Mexico_City')
        mx_time = timezone.fromutc(datetime_val)
        return mx_time.strftime("%d-%b-%Y %H:%M").replace('.', '')
    else:
        return ""


def send_csv(iterable, filename, fields=None, schema=None, delimiter=',',
             encoding='utf-8', writer_kwargs=None, **kwargs):
    buf = StringIO()
    writer_cls = ValidatedWriter
    if schema:
        writer_cls = ValidatedWriter.from_schema(schema)
    writer_kwargs = writer_kwargs or {}
    writer = writer_cls(buf, fields, delimiter=delimiter, **writer_kwargs)
    writer.writeheader()
    for line in iterable:
        writer.writerow(line)
    buf.seek(0)
    buf = BytesIO(buf.read().encode('utf_8_sig'))
    mimetype = 'Content-Type: text/csv; charset='+encoding
    return send_file(buf, download_name=filename, as_attachment=True,
                     mimetype=mimetype, **kwargs)
