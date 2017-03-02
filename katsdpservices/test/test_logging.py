"""Tests for :mod:`katsdpservices.logging`"""

from __future__ import print_function, division, absolute_import
import time
import logging
import os
import re
import mock
import unittest2 as unittest
import six
import katsdpservices


class TestLogging(unittest.TestCase):
    def _create_patch(self, *args, **kwargs):
        patcher = mock.patch(*args, **kwargs)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj

    def _create_patch_dict(self, *args, **kwargs):
        patcher = mock.patch.dict(*args, **kwargs)
        mock_obj = patcher.start()
        self.addCleanup(patcher.stop)
        return mock_obj

    def setUp(self):
        # Grab the stderr written by the logger
        self.stderr = self._create_patch('sys.stderr', new_callable=six.StringIO)
        # Point root away from the actual root logger, so that we don't break
        # that.
        self.logger = self._create_patch('logging.root', logging.getLogger('katsdpservices.test.dummy'))
        # Wipe out existing environment, so that we can poke KATSDP_LOG_*
        self.environ = self._create_patch_dict(os.environ, clear=True)
        # Override time so that we can compare against a known value
        self.time = self._create_patch('time.time', autospec=True)
        self.time.return_value = 1488463323.125

    def test_simple(self):
        katsdpservices.setup_logging()
        logging.debug('debug message')
        logging.info('info message')
        logging.warning('warning message\nwith\nnewlines')
        self.assertRegex(
            self.stderr.getvalue(),
            re.compile(
                "\\A2017-03-02T14:02:03.125Z - test_logging.py:\\d+ - INFO - info message\n"
                "2017-03-02T14:02:03.125Z - test_logging.py:\\d+ - WARNING - warning message\n"
                "with\n"
                "newlines\n\\Z", re.M))

    def test_one_line(self):
        os.environ['KATSDP_LOG_ONELINE'] = '1'
        katsdpservices.setup_logging()
        logging.debug('debug message')
        logging.info('info message')
        logging.warning('warning message\nwith\nnewlines')
        # The \\\\ in the regex is a literal \: one level of escaping for
        # Python, one for regex.
        self.assertRegex(
            self.stderr.getvalue(),
            re.compile(
                "\\A2017-03-02T14:02:03.125Z - test_logging.py:\\d+ - INFO - info message\n"
                "2017-03-02T14:02:03.125Z - test_logging.py:\\d+ - WARNING - warning message\\\\ "
                "with\\\\ "
                "newlines\n\Z", re.M))

    def test_log_level(self):
        os.environ['KATSDP_LOG_LEVEL'] = 'debug'
        katsdpservices.setup_logging()
        logging.debug('debug message')
        logging.info('info message')
        logging.warning('warning message\nwith\nnewlines')
        self.assertRegex(
            self.stderr.getvalue(),
            re.compile(
                "\\A2017-03-02T14:02:03.125Z - test_logging.py:\\d+ - DEBUG - debug message\n"
                "2017-03-02T14:02:03.125Z - test_logging.py:\\d+ - INFO - info message\n"
                "2017-03-02T14:02:03.125Z - test_logging.py:\\d+ - WARNING - warning message\n"
                "with\n"
                "newlines\n\\Z", re.M))
