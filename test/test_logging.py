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

"""Tests for :mod:`katsdpservices.logging`"""

import io
import json
import logging
import os
import re
import signal
import socket
import sys
import time
import unittest
import zlib
from contextlib import closing
from unittest import mock

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

    def _wipe_dummy_logger(self):
        logger = logging.getLogger('katsdpservices.test.dummy')
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        for filter in list(logger.filters):
            logger.removeFilter(filter)

    def setUp(self):
        # Grab the stderr written by the logger
        self.stderr = self._create_patch('sys.stderr', new_callable=io.StringIO)
        # Point root away from the actual root logger, so that we don't break
        # that.
        self.logger = self._create_patch(
            'logging.root', logging.getLogger('katsdpservices.test.dummy'))
        self.addCleanup(self._wipe_dummy_logger)
        # Wipe out existing environment, so that we can poke KATSDP_LOG_*
        self.environ = self._create_patch_dict(os.environ, clear=True)
        # Override time so that we can compare against a known value
        self.time = self._create_patch('time.time', autospec=True)
        self.time.return_value = 1488463323.125125
        self.addCleanup(signal.signal, signal.SIGHUP, signal.SIG_DFL)

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
                "newlines\n\\Z", re.M))

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

    def _test_gelf(self, localname, extra):
        self.maxDiff = 4096   # Diff tends to be too big to display otherwise
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        with closing(sock):
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
            os.environ['KATSDP_LOG_GELF_ADDRESS'] = '127.0.0.1:{}'.format(port)
            if localname:
                os.environ['KATSDP_LOG_GELF_LOCALNAME'] = 'myhost'
            if extra:
                os.environ['KATSDP_LOG_GELF_EXTRA'] = '{"hello": "world", "number": 3}'
            # Fake the container ID
            container_id = "abcdef0123456789"
            with mock.patch('katsdpservices.logging.docker_container_id',
                            return_value=container_id):
                katsdpservices.setup_logging()
            # exc_info=False is to test the fix for
            # https://github.com/keeprocking/pygelf/issues/29
            logging.info('info message', exc_info=False)
            raw = sock.recv(4096)
            raw = zlib.decompress(raw)
        data = json.loads(raw.decode('utf-8'))
        # This dictionary may need to be updated depending on the implementation
        expected = {
            "timestamp": self.time.return_value,
            "version": "1.1",
            "short_message": "info message",
            "_logger_name": "katsdpservices.test.dummy",
            "_file": mock.ANY,
            "_line": mock.ANY,
            "_func": "_test_gelf",
            "_module": "test_logging",
            "_docker.id": container_id,
            "_timestamp_precise": "2017-03-02T14:02:03.125125Z",
            "level": 6,
            "host": "myhost" if localname else mock.ANY
        }
        if extra:
            expected["_hello"] = "world"
            expected["_number"] = 3
        expected["_stack_info"] = None
        if sys.version_info >= (3, 12, 0):
            expected["_taskName"] = None
        self.assertEqual(data, expected)

    def test_gelf_basic(self):
        self._test_gelf(False, False)

    def test_gelf_options(self):
        self._test_gelf(True, True)

    def test_toggle_debug(self):
        self.assertEqual(logging.INFO, logging.root.level)
        os.kill(os.getpid(), signal.SIGUSR2)
        # Give it a bit of time, since it's done in a separate thread
        time.sleep(0.01)
        self.assertEqual(logging.DEBUG, logging.root.level)
        # Check that it toggles back again
        os.kill(os.getpid(), signal.SIGUSR2)
        time.sleep(0.01)
        self.assertEqual(logging.INFO, logging.root.level)
