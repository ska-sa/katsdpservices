"""Tests for :mod:`katsdpservices.aiomonitor`.

This file needs to load correctly in Python 2, which is why some
imports are delayed.
"""

import unittest

import mock
import six

from .. import ArgumentParser, start_aiomonitor


@unittest.skipIf(six.PY2, 'Only supported on Python 3')
class TestStartAiomonitor(unittest.TestCase):
    def setUp(self):
        import asyncio

        self.parser = ArgumentParser()
        self.parser.add_aiomonitor_arguments()
        patcher = mock.patch('aiomonitor.start_monitor')
        self.mock_start = patcher.start()
        self.addCleanup(patcher.stop)
        self.loop = asyncio.new_event_loop()

    def test_no_aiomonitor(self):
        args = self.parser.parse_args(['--no-aiomonitor'])
        with start_aiomonitor(self.loop, args, locals()):
            pass
        self.mock_start.assert_not_called()

    def test_defaults(self):
        import aiomonitor

        args = self.parser.parse_args([])
        locals_ = {'hello': 'world'}
        with start_aiomonitor(self.loop, args, locals_):
            pass
        self.mock_start.assert_called_once_with(
            loop=self.loop, host=aiomonitor.MONITOR_HOST,
            port=aiomonitor.MONITOR_PORT,
            console_port=aiomonitor.CONSOLE_PORT,
            locals=locals_)

    def test_explicit(self):
        args = self.parser.parse_args(
            ['--aiomonitor-host', 'example.com',
             '--aiomonitor-port', '1234',
             '--aioconsole-port', '2345'])
        locals_ = {'hello': 'world'}
        with start_aiomonitor(self.loop, args, locals_):
            pass
        self.mock_start.assert_called_once_with(
            loop=self.loop, host='example.com',
            port=1234,
            console_port=2345,
            locals=locals_)
