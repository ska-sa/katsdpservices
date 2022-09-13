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

"""Utility to make the process restart itself on SIGHUP"""

import sys
import os.path
import fcntl
import signal
import logging
import threading


# Latch the absolute path now, in case something changes directory later
# and makes a relative path invalid.
_restart_args = list(sys.argv)
_restart_args[0] = os.path.abspath(sys.argv[0])
_logger = logging.getLogger(__name__)


def restart_process():
    """Re-exec the process with its original arguments"""
    # Set file handles to close on exec, so that sockets don't live on
    # and prevent us opening the ports again.
    try:
        for name in os.listdir('/proc/self/fd'):
            try:
                fd = int(name)
            except ValueError:
                pass
            else:
                if fd > 2:   # Don't close stdin/stdout/stderr
                    try:
                        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
                        fcntl.fcntl(fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
                    except OSError:
                        # This is guaranteed to happen, because the fd used by
                        # os.listdir will be in the list, but is closed by the
                        # time we try to change the flags on it.
                        pass
    except OSError:
        logging.warn('Could not read /proc/self/fd')
    # Ensure any logging gets properly flushed
    sys.stdout.flush()
    sys.stderr.flush()
    os.execlp(sys.executable, sys.executable, *_restart_args)


def setup_restart(signum=signal.SIGHUP, restart_callback=None):
    """Install a signal handler that calls :func:`restart` when :const:`SIGHUP`
    is received.

    Parameters
    ----------
    signum : int, optional
        Signum number for the signal handler to install
    restart_callback : callable
        If specified, this is called before execing. This can be used
        to cleanly wind up state. If it returns a true value, the restart is
        not done. This can be used if the callback just schedules cleanup and
        :func:`restart_process` in an asynchronous manner.
    """
    def restart_thread():
        logger = logging.getLogger(__file__)
        logger.warning("Received signal %d, restarting", signum)
        if restart_callback is not None:
            if restart_callback():
                return
        restart_process()

    def restart_handler(signum, frame):
        # It's not safe to log directly from a signal handler, so start
        # a separate thread to do the shutdown.
        thread = threading.Thread(target=restart_thread)
        thread.daemon = True
        thread.start()
    signal.signal(signal.SIGHUP, restart_handler)
