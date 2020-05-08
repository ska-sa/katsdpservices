################################################################################
# Copyright (c) 2017-2020, National Research Foundation (Square Kilometre Array)
#
# Licensed under the BSD 3-Clause License (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy
# of the License at
#
#   https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

r"""Customised SDP logging

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
received, and exception hooks are installed so that unhandled exceptions are
logged rather than merely printing to stderr.
"""

import logging
import os
import sys
import re
import time
import signal
import threading
import json

import pygelf


_toggle_next_level = logging.DEBUG
"""Log level to set on next call to :func:`toggle_debug`."""


class OnelineFormatter(logging.Formatter):
    r"""Formatting that encodes newlines so that a single log message always
    appears on a single line. Newlines are replaced by "\ "  and backslashes
    are replaced by "\\".
    """
    def format(self, record):
        s = super().format(record)
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


def docker_container_id():
    """Find the container ID of the current container.

    If not running in a container, returns ``None``.
    """
    regex = re.compile(':/docker/([a-f0-9]+)$')
    try:
        with open("/proc/self/cgroup") as f:
            for line in f:
                match = regex.search(line)
                if match:
                    return match.group(1)
    except OSError:
        pass
    return None


def _setup_logging_gelf():
    parts = os.environ['KATSDP_LOG_GELF_ADDRESS'].rsplit(':', 1)
    host = parts[0]
    if len(parts) == 2:
        port = int(parts[1])
    else:
        port = 12201     # Default GELF port
    localname = os.environ.get('KATSDP_LOG_GELF_LOCALNAME')
    extras = os.environ.get('KATSDP_LOG_GELF_EXTRA', '{}')
    extras = json.loads(extras)
    if not isinstance(extras, dict):
        raise ValueError('KATSDP_LOG_GELF_EXTRA must be a JSON dict')
    # pygelf wants the additional fields to have _ already prepended
    extras = {'_' + key: value for (key, value) in extras.items()}
    container_id = docker_container_id()
    if container_id is not None:
        extras['_docker.id'] = container_id

    handler = pygelf.GelfUdpHandler(host, port,
                                    debug=True, include_extra_fields=True, compress=True,
                                    static_fields=extras)
    if localname:
        handler.domain = localname
    logging.root.addHandler(handler)


def _sys_excepthook(exc_type, exc_value, exc_traceback):
    logging.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


def _threading_excepthook(args):
    if args.exc_type == SystemExit:
        return      # To match the behaviour of the default
    if logging is None or threading is None:
        return      # We're deep into interpreter shutdown - just give up

    # Based on Python 3.8 implementation: https://github.com/python/cpython/pull/13515
    if args.thread is not None:
        name = args.thread.name
    else:
        name = threading.get_ident()
    logging.error("Exception in thread {}:".format(name),
                  exc_info=(args.exc_type, args.exc_value, args.exc_traceback))


def setup_logging(add_signal_handler=True, add_excepthook=True):
    """Prepare logging. See the module-level documentation for details."""
    if os.environ.get('KATSDP_LOG_GELF_ADDRESS'):
        _setup_logging_gelf()
    _setup_logging_stderr()
    if 'KATSDP_LOG_LEVEL' in os.environ:
        logging.root.setLevel(os.environ['KATSDP_LOG_LEVEL'].upper())
    else:
        logging.root.setLevel(logging.INFO)
    logging.captureWarnings(True)
    if add_signal_handler:
        signal.signal(signal.SIGUSR2, lambda signum, frame: toggle_debug())
    if add_excepthook:
        sys.excepthook = _sys_excepthook
        # Only supported from Python 3.8
        if hasattr(threading, 'excepthook'):
            threading.excepthook = _threading_excepthook
