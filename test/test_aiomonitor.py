################################################################################
# Copyright (c) 2017-2020, 2022, 2024 National Research Foundation (SARAO)
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

"""Tests for :mod:`katsdpservices.aiomonitor`."""

import asyncio
import unittest
from unittest import mock

import aiomonitor

from katsdpservices import ArgumentParser, start_aiomonitor, add_aiomonitor_arguments


class TestStartAiomonitor(unittest.TestCase):
    def setUp(self):
        self.parser = ArgumentParser()
        add_aiomonitor_arguments(self.parser)
        patcher = mock.patch('aiomonitor.start_monitor', autospec=True)
        self.mock_start = patcher.start()
        self.addCleanup(patcher.stop)
        self.loop = asyncio.new_event_loop()

    def test_no_aiomonitor(self):
        args = self.parser.parse_args([])
        with start_aiomonitor(self.loop, args, locals()):
            pass
        self.mock_start.assert_not_called()

    def test_defaults(self):
        args = self.parser.parse_args(['--aiomonitor'])
        locals_ = {'hello': 'world'}
        with start_aiomonitor(self.loop, args, locals_):
            pass
        self.mock_start.assert_called_once_with(
            loop=self.loop, host=aiomonitor.MONITOR_HOST,
            port=aiomonitor.MONITOR_PORT,
            console_port=aiomonitor.CONSOLE_PORT,
            webui_port=aiomonitor.MONITOR_WEBUI_PORT,
            locals=locals_)

    def test_explicit(self):
        args = self.parser.parse_args(
            ['--aiomonitor',
             '--aiomonitor-host', 'example.com',
             '--aiomonitor-port', '1234',
             '--aiomonitor-webui-port', '4321',
             '--aioconsole-port', '2345'])
        locals_ = {'hello': 'world'}
        with start_aiomonitor(self.loop, args, locals_):
            pass
        self.mock_start.assert_called_once_with(
            loop=self.loop, host='example.com',
            port=1234,
            console_port=2345,
            webui_port=4321,
            locals=locals_)
