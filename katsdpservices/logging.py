"""Customised SDP logging

Logging is controlled by environment variables:

KATSDP_LOG_ONELINE: if set (to any value), newlines in log messages are escaped
  to fit the message onto a single line (see :class:`OnelineFormatter`).
KATSDP_LOG_LEVEL: if set, it is used as the name of the log level. Otherwise,
  the log level defaults to INFO.
KATSDP_LOG_GELF_ADDRESS: if set (to a host:port), logging is sent over UDP
  to this address in Graylog Extended Logging Format.
KATSDP_LOG_GELF_LOCALNAME: if set, this overrides the local system name used
  in GELF log messages
KATSDP_LOG_GELF_EXTRA: set to a JSON dictionary (containing only strings and
  numbers, and with keys matching ``^[\w\.\-]*$``) of extra values to pass in
  every log message.

A signal handler is installed that toggles debug-level logging when SIGUSR2 is
received.
"""

from __future__ import print_function, division, absolute_import
import logging
import os
import time
import signal
import threading
import json

import graypy


_toggle_next_level = logging.DEBUG
"""Log level to set on next call to :func:`toggle_debug`."""


class OnelineFormatter(logging.Formatter):
    r"""Formatting that encodes newlines so that a single log message always
    appears on a single line. Newlines are replaced by "\ "  and backslashes
    are replaced by "\\".
    """
    def format(self, record):
        s = super(OnelineFormatter, self).format(record)
        return s.replace('\\', r'\\').replace('\n', r'\ ')


def toggle_debug():
    """Swap current log level with the saved log level."""
    global _toggle_next_level
    old = logging.root.level
    logging.info(
        'Changing log level from %s to %s',
        logging.getLevelName(old), logging.getLevelName(_toggle_next_level))
    logging.root.setLevel(_toggle_next_level)
    _toggle_next_level = old


def _toggle_debug_handler(signum, frame):
    """Signal handler that calls :func:`toggle_debug` asynchronously.

    It's not safe to manipulate logging if the signal was received during a
    logging call. Instead, start a separate thread, and rely on logging's
    locking to do this change safely.
    """
    thread = threading.Thread(target=toggle_debug)
    thread.daemon = True
    thread.start()


def _setup_logging_stderr():
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


class StaticExtraFilter(logging.Filter):
    """Filter that adds preconfigured fields to all log records"""
    def __init__(self, extra):
        self._extra = extra

    def filter(self, record):
        for key, value in self._extra.items():
            setattr(record, key, value)
        return record


def _setup_logging_gelf():
    parts = os.environ['KATSDP_LOG_GELF_ADDRESS'].rsplit(':', 1)
    host = parts[0]
    if len(parts) == 2:
        port = int(parts[1])
    else:
        port = 12201     # Default GELF port
    localname = os.environ.get('KATSDP_LOG_GELF_LOCALNAME')
    handler = graypy.GELFHandler(host, port, localname=localname)
    logging.root.addHandler(handler)

    extras = os.environ.get('KATSDP_LOG_GELF_EXTRA', '{}')
    extras = json.loads(extras)
    if not isinstance(extras, dict):
        raise ValueError('KATSDP_LOG_GELF_EXTRA must be a JSON dict')
    if extras:
        handler.addFilter(StaticExtraFilter(extras))


def setup_logging(add_signal_handler=True):
    """Prepare logging. See the module-level documentation for details."""
    if 'KATSDP_LOG_GELF_ADDRESS' in os.environ:
        _setup_logging_gelf()
    _setup_logging_stderr()
    if 'KATSDP_LOG_LEVEL' in os.environ:
        logging.root.setLevel(os.environ['KATSDP_LOG_LEVEL'].upper())
    else:
        logging.root.setLevel(logging.INFO)
    logging.captureWarnings(True)
    if add_signal_handler:
        signal.signal(signal.SIGUSR2, lambda signum, frame: toggle_debug())
