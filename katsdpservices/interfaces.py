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
    interface : str
        Name of the network interface

    Returns
    -------
    address : str
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
