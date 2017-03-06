"""Customised SDP logging

Logging is controlled by environment variables:

KATSDP_LOG_ONELINE: if set (to any value), newlines in log messages are escaped
  to fit the message onto a single line (see :class:`OnelineFormatter`).
KATSDP_LOG_LEVEL: if set, it is used as the name of the log level. Otherwise,
  the log level defaults to INFO.

A signal handler is installed that toggles debug-level logging when SIGUSR2 is
received.
"""

from __future__ import print_function, division, absolute_import
import logging
import os
import time
import signal
import threading


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


def setup_logging(add_signal_handler=True):
    """Prepare logging. See the module-level documentation for details."""
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
    logging.captureWarnings(True)
    if add_signal_handler:
        signal.signal(signal.SIGUSR2, lambda signum, frame: toggle_debug())
