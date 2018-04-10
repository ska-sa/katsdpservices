"""Tests for :mod:`katsdpservices.interfaces`."""

import mock
import unittest
import netifaces
from katsdpservices import get_interface_address


class TestGetInterfaceAddress(unittest.TestCase):
    def test_none(self):
        """Passing None returns None"""
        self.assertIsNone(get_interface_address(None))

    def test_invalid(self):
        """Passing a non-existent interface raises :exc:`ValueError`"""
        with self.assertRaises(ValueError):
            get_interface_address('not_an_interface_name')

    def test_no_ipv4(self):
        """An interface with no IPv4 entries raises :exc:`ValueError`"""
        with mock.patch('netifaces.ifaddresses', return_value={
            netifaces.AF_LINK: [{'addr': 'de:ad:be:ef:ca:fe', 'broadcast': 'ff:ff:ff:ff:ff:ff'}]
        }):
            with self.assertRaises(ValueError):
                get_interface_address('wlan1')

    def test_valid(self):
        with mock.patch('netifaces.ifaddresses', return_value={
            netifaces.AF_LINK: [{'addr': 'de:ad:be:ef:ca:fe', 'broadcast': 'ff:ff:ff:ff:ff:ff'}],
            netifaces.AF_INET: [{'addr': '192.168.1.1', 'broadcast': '192.168.1.255',
                                 'netmask': '255.255.255.0'}]
        }) as m:
            self.assertEqual('192.168.1.1', get_interface_address('eth1'))
            m.assert_called_with('eth1')
