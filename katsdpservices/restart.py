"""Utility to make the process restart itself on SIGHUP"""
from __future__ import print_function, division, absolute_import
import sys
import os.path
import signal
import logging
import threading


# Latch the absolute path now, in case something changes directory later
# and makes a relative path invalid.
_restart_args = list(sys.argv)
_restart_args[0] = os.path.abspath(sys.argv[0])


def restart_process():
    """Re-exec the process with its original arguments"""
    # Ensure any logging gets properly flushed
    sys.stdout.flush()
    sys.stderr.flush()
    os.execlp(sys.executable, _restart_args[0], *_restart_args)


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
        logger.warn("Received signal %d, restarting", signum)
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
