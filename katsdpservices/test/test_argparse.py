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

"""Tests for :mod:`katsdpservices.argparse`."""

import unittest
from unittest import mock

from katsdpservices import ArgumentParser


class MockException(Exception):
    """Exception class used for monkey-patching functions that don't return."""
    pass


class TestArgumentParser(unittest.TestCase):
    def _stub_get(self, name, default=None):
        return self.data.get(name, default)

    def setUp(self):
        # Set up a mock version of TelescopeState which applies for the whole test
        patcher = mock.patch('katsdptelstate.TelescopeState', autospec=True)
        self.addCleanup(patcher.stop)
        self.TelescopeState = patcher.start()
        self.TelescopeState.return_value.get = mock.MagicMock(side_effect=self._stub_get)
        # Create a fixture
        self.parser = ArgumentParser()
        self.parser.add_argument('positional', type=str)
        self.parser.add_argument('--int-arg', type=int, default=5)
        self.parser.add_argument('--float-arg', type=float, default=3.5)
        self.parser.add_argument('--no-default', type=str)
        self.parser.add_argument('--bool-arg', action='store_true', default=False)
        group = self.parser.add_argument_group('Group options')
        group.add_argument('--group-int', type=int, default=6)
        mutual = self.parser.add_mutually_exclusive_group()
        mutual.add_argument('--mutual-x', default='x')
        mutual.add_argument('--mutual-y', default='y')
        self.data = {
            'config': {
                'int_arg': 10,
                'float_arg': 4.5,
                'no_default': 'telstate',
                'bool_arg': True,
                'not_arg': 'should not be seen',
                'telstate': 'example.org',
                'group_int': 11,
                'mutual_y': 'z',
                'level1': {
                    'int_arg': 11,
                    'level2': {
                        'float_arg': 5.5
                    }
                }
            },
            'config.level1.level2': {
                'float_arg': 12.5
            }
        }

    def test_no_telstate(self):
        """Passing explicit arguments but no telescope model sets the arguments."""
        args = self.parser.parse_args(
            ['hello', '--int-arg=3', '--float-arg=2.5', '--no-default=test', '--bool-arg',
             '--group-int=11', '--mutual-y=z'])
        self.assertIsNone(args.telstate)
        self.assertEqual('', args.name)
        self.assertEqual('hello', args.positional)
        self.assertEqual(3, args.int_arg)
        self.assertEqual(2.5, args.float_arg)
        self.assertEqual('test', args.no_default)
        self.assertEqual(True, args.bool_arg)
        self.assertEqual(11, args.group_int)
        self.assertEqual('z', args.mutual_y)

    def test_no_telstate_defaults(self):
        """Passing no optional arguments sets those arguments to default"""
        args = self.parser.parse_args(['hello'])
        self.assertIsNone(args.telstate)
        self.assertEqual('', args.name)
        self.assertEqual('hello', args.positional)
        self.assertEqual(5, args.int_arg)
        self.assertEqual(3.5, args.float_arg)
        self.assertIsNone(args.no_default)
        self.assertEqual(False, args.bool_arg)
        self.assertEqual(6, args.group_int)
        self.assertEqual('y', args.mutual_y)

    def test_telstate_no_name(self):
        """Passing --telstate but not --name loads from root config"""
        args = self.parser.parse_args(['hello', '--telstate=example.com'])
        self.assertIs(self.TelescopeState.return_value, args.telstate)
        self.assertEqual('', args.name)
        self.assertEqual(10, args.int_arg)
        self.assertEqual(4.5, args.float_arg)
        self.assertEqual('telstate', args.no_default)
        self.assertEqual(True, args.bool_arg)
        self.assertEqual(11, args.group_int)
        self.assertEqual('z', args.mutual_y)
        self.assertNotIn('help', vars(args))
        self.assertNotIn('not_arg', vars(args))

    def test_telstate_nested(self):
        """Passing a nested name loads from all levels of the hierarchy"""
        args = self.parser.parse_args(['hello', '--telstate=example.com', '--name=level1.level2'])
        self.assertIs(self.TelescopeState.return_value, args.telstate)
        self.assertEqual('level1.level2', args.name)
        self.assertEqual('hello', args.positional)
        self.assertEqual(11, args.int_arg)
        self.assertEqual(12.5, args.float_arg)
        self.assertEqual('telstate', args.no_default)

    def test_telstate_override(self):
        """Command-line parameters override telescope state"""
        args = self.parser.parse_args(
            ['hello', '--int-arg=0', '--float-arg=0', '--telstate=example.com',
             '--name=level1.level2', '--group-int=15'])
        self.assertIs(self.TelescopeState.return_value, args.telstate)
        self.assertEqual('level1.level2', args.name)
        self.assertEqual('hello', args.positional)
        self.assertEqual(0, args.int_arg)
        self.assertEqual(0.0, args.float_arg)
        self.assertEqual('telstate', args.no_default)
        self.assertEqual(15, args.group_int)

    def test_default_telstate(self):
        """Calling `set_default` with `telstate` keyword works"""
        self.parser.set_defaults(telstate='example.com')
        args = self.parser.parse_args(['hello'])
        self.TelescopeState.assert_called_once_with('example.com')
        self.assertIs(self.TelescopeState.return_value, args.telstate)
        self.assertEqual(10, args.int_arg)

    def test_convert_argument(self):
        """String argument in telescope state that must be converted to the appropriate type."""
        self.data['config']['int_arg'] = '50'
        args = self.parser.parse_args(['--telstate=example.com', 'hello'])
        self.assertEqual(50, args.int_arg)

    def test_bad_argument(self):
        """String argument in telescope state that cannot be converted must raise an error."""
        self.data['config']['int_arg'] = 'not an int'
        # We make the mock raise an exception, since the patched code is not
        # expecting the function to return.
        with mock.patch.object(
                self.parser, 'error', autospec=True, side_effect=MockException) as mock_error:
            with self.assertRaises(MockException):
                self.parser.parse_args(['--telstate=example.com', 'hello'])
            mock_error.assert_called_once_with(mock.ANY)

    def test_help(self):
        """Passing --help prints help without trying to construct the telescope state"""
        # We make the mock raise an exception, since the patched code is not
        # expecting the function to return.
        with mock.patch.object(
                self.parser, 'exit', autospec=True, side_effect=MockException) as mock_exit:
            with self.assertRaises(MockException):
                self.parser.parse_args(['--telstate=example.com', '--help'])
            mock_exit.assert_called_once_with()
            # Make sure we did not try to construct a telescope state
            self.assertEqual([], self.TelescopeState.call_args_list)
