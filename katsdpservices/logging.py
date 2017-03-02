"""Customised SDP logging

Logging is controlled by environment variables:

KATSDP_LOG_ONELINE: if set (to any value), newlines in log messages are escaped
  to fit the message onto a single line (see :class:`OnelineFormatter`).
KATSDP_LOG_LEVEL: if set, it is used as the name of the log level. Otherwise,
  the log level defaults to INFO.
"""

from __future__ import print_function, division, absolute_import
import logging
import os
import time


class OnelineFormatter(logging.Formatter):
    r"""Formatting that encodes newlines so that a single log message always
    appears on a single line. Newlines are replaced by "\ "  and backslashes
    are replaced by "\\".
    """
    def format(self, record):
        s = super(OnelineFormatter, self).format(record)
        return s.replace('\\', r'\\').replace('\n', r'\ ')


def setup_logging():
    if 'KATSDP_LOG_ONELINE' in os.environ:
        formatter_class = OnelineFormatter
    else:
        formatter_class = logging.Formatter
    formatter = formatter_class(
        "%(asctime)s.%(msecs)03dZ - %(filename)s:%(lineno)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S")
    formatter.converter = time.gmtime
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logging.root.addHandler(sh)
    if 'KATSDP_LOG_LEVEL' in os.environ:
        logging.root.setLevel(os.environ['KATSDP_LOG_LEVEL'].upper())
    else:
        logging.root.setLevel(logging.INFO)
