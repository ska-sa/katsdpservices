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

"""Simple utility functions to access information about network interfaces.

This is a simple wrapper around :mod:`netifaces`.
"""

import netifaces


def get_interface_address(interface):
    """Obtain the IPv4 address of a network interface.

    If the interface has multiple IPv4 addresses, it returns the first one.
    As a convenience, it is legal to pass ``None`` as the address, in which
    case ``None`` is returned.

    Parameters
    ----------
    interface : str | None
        Name of the network interface

    Returns
    -------
    address : str | None
        Dotted-quad representation of the IPv4 address

    Raises
    ------
    ValueError
        if the interface does not exist or does not have an IPv4 address
    """
    if interface is None:
        return None
    else:
        try:
            return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        except (IndexError, KeyError):
            raise ValueError('No IPv4 address found for interface ' + interface)
