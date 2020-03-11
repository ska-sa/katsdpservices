"""Tests for :mod:`katsdpservices.restart`"""

from __future__ import print_function, division, absolute_import
import mock
import os
import signal
import time
import unittest
import katsdpservices


class TestRestart(unittest.TestCase):
    def _create_patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj

    def setUp(self):
        self.execlp = self._create_patch('os.execlp', spec=True)
        self.addCleanup(signal.signal, signal.SIGHUP, signal.SIG_DFL)

    def test_restart(self):
        katsdpservices.restart_process()
        # assert_called_once_with can't specify an unknown number of arguments
        self.assertEqual(1, len(self.execlp.mock_calls))

    def test_restart_signal(self):
        katsdpservices.setup_restart()
        os.kill(os.getpid(), signal.SIGHUP)
        # Give time for asynchronous handling
        time.sleep(0.01)
        self.assertEqual(1, len(self.execlp.mock_calls))

    def test_restart_signal_with_false_callback(self):
        callback = mock.MagicMock()
        callback.return_value = False
        katsdpservices.setup_restart(restart_callback=callback)
        os.kill(os.getpid(), signal.SIGHUP)
        # Give time for asynchronous handling
        time.sleep(0.01)
        callback.assert_called_once_with()
        self.assertEqual(1, len(self.execlp.mock_calls))

    def test_restart_signal_with_true_callback(self):
        callback = mock.MagicMock()
        callback.return_value = True
        katsdpservices.setup_restart(restart_callback=callback)
        os.kill(os.getpid(), signal.SIGHUP)
        # Give time for asynchronous handling
        time.sleep(0.01)
        callback.assert_called_once_with()
        self.execlp.assert_not_called()
