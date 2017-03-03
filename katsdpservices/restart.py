"""Utility to make the process restart itself on SIGHUP"""
from __future__ import print_function, division, absolute_import
import sys
import os.path
import signal
import logging


def setup_restart(signum=signal.SIGHUP, restart_callback=None):
    """Install a signal handler that makes the process exec itself when
    SIGHUP is received.

    Parameters
    ----------
    signum : int, optional
        Signum number for the signal handler to install
    restart_callback : callable
        If specified, this is called before calling execing. This can be used
        to cleanly wind up state.

    Returns
    -------
    restart : callable
        Function that restarts the process
    """
    def restart():
        if restart_callback is not None:
            restart_callback()
        # Ensure any logging gets properly flushed
        sys.stdout.flush()
        sys.stderr.flush()
        os.execlp(sys.executable, args[0], *args)
    def restart_handler(signum, frame):
        logger = logging.getLogger(__file__)
        logger.warn("Received signal %d, restarting", signum)
        restart()
    # Latch the absolute path now, in case something changes directory later
    # and makes a relative path invalid.
    args = list(sys.argv)
    args[0] = os.path.abspath(args[0])
    signal.signal(signal.SIGHUP, restart_handler)
    return restart
