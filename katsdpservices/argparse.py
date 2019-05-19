"""Argument parser that can load defaults from a telescope state.

See :class:`ArgumentParser` for details.
"""

from __future__ import print_function, division, absolute_import
import argparse
try:
    import katsdptelstate
except ImportError:
    pass


class _HelpAction(argparse.Action):
    """Class modelled on argparse._HelpAction that prints help for the
    main parser."""
    def __init__(self,
                 option_strings,
                 parser,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help=None):
        super(_HelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)
        self._parser = parser

    def __call__(self, parser, namespace, values, option_string=None):
        self._parser.print_help()
        self._parser.exit()


class ArgumentParser(argparse.ArgumentParser):
    """Argument parser that can load defaults from a telescope state. It can be
    used as a drop-in replacement for `argparse.ArgumentParser`. It adds the
    options `--telstate` and `--name`. The first takes the hostname of a
    telescope state repository (optionally with a port). If specified,
    `parse_args` will first connect to this host and fetch defaults (which
    override the defaults specified by `add_argument`). The telescope state
    will also be available in the returned `argparse.Namespace`.

    If `name` is specified, it consists of a dot-separated list of
    identifiers, specifying a path through a tree of dictionaries of config.
    For example, `foo.0` will cause configuration to be searched in
    `config`, `config["foo"]`, `config["foo"]["0"]`, `config.foo` and
    `config.foo.0`. If configuration is found in multiple places, the most
    specific location will be used first, breaking ties to use `config.*`
    in preference to embedded dictionaries within `config`. It is not an error
    for one of these dictionaries not to exist, but it is an error if a name is
    found but is not a dictionary.

    New code generating config dictionaries is advised to use the `config.*`
    form, as it is more scalable (no need to fetch unrelated config).
    Sub-config embedded within `config` is supported for backwards
    compatibility.

    A side-effect of the implementation is that calling `parse_args` or
    `parse_known_args` permanently changes the defaults. A parser should thus
    only be used once and then thrown away. Also, because it changes the
    defaults rather than injecting actual arguments, argparse features like
    required arguments and mutually exclusive groups might not work as
    expected.

    Parameters
    ----------
    config_key : str, optional
        Name of the config dictionary within the telescope state (default: `config`)
    """

    _SPECIAL_NAMES = ['telstate', 'name']

    def __init__(self, *args, **kwargs):
        self.config_key = kwargs.pop('config_key', 'config')
        super(ArgumentParser, self).__init__(*args, **kwargs)
        # Create a separate parser that will extract only the special args
        self.config_parser = argparse.ArgumentParser(add_help=False)
        self.config_parser.add_argument('-h', '--help', action=_HelpAction,
                                        default=argparse.SUPPRESS, parser=self)
        for parser in [super(ArgumentParser, self), self.config_parser]:
            parser.add_argument(
                '--telstate', help='Telescope state repository from which to retrieve config',
                metavar='HOST[:PORT]')
            parser.add_argument(
                '--name', type=str, default='',
                help='Name of this process for telescope state configuration')

    def _valid_keys(self):
        """Get set of keys that match defined arguments"""
        # _actions is a private member of the base class! But trying to avoid
        # accessing this is quite difficult if one wishes to handle cases like
        # :meth:`add_argument_group` and :meth:`add_mutually_exclusive_group`,
        # parent parsers etc.
        bad_names = [None, argparse.SUPPRESS, 'help'] + self._SPECIAL_NAMES
        return set(action.dest for action in self._actions if action.dest not in bad_names)

    def _load_defaults(self, telstate, name):
        config_dict = telstate.get(self.config_key, {})
        parts = name.split('.')
        cur = config_dict
        config = cur.copy()
        split_name = self.config_key
        for part in parts:
            if cur is not None:
                cur = cur.get(part)
                if cur is not None:
                    config.update(cur)
            split_name += '.'
            split_name += part
            config.update(telstate.get(split_name, {}))

        valid_keys = self._valid_keys()
        defaults = {key: value for key, value in config.items() if key in valid_keys}
        super(ArgumentParser, self).set_defaults(**defaults)

    def set_defaults(self, **kwargs):
        for special in self._SPECIAL_NAMES:
            if special in kwargs:
                self.config_parser.set_defaults(**{special: kwargs.pop(special)})
        super(ArgumentParser, self).set_defaults(**kwargs)

    def parse_known_args(self, args=None, namespace=None):
        if namespace is None:
            namespace = argparse.Namespace()
        try:
            config_args, other = self.config_parser.parse_known_args(args)
        except argparse.ArgumentError:
            other = args
        else:
            if config_args.telstate is not None:
                try:
                    namespace.telstate = katsdptelstate.TelescopeState(config_args.telstate)
                except katsdptelstate.ConnectionError as e:
                    self.error(str(e))
                namespace.name = config_args.name
                self._load_defaults(namespace.telstate, namespace.name)
        return super(ArgumentParser, self).parse_known_args(other, namespace)

    def add_aiomonitor_arguments(self):
        """Add a set of arguments for controlling aiomonitor.

        See :func:`.start_aiomonitor` for details.
        """
        import aiomonitor
        self.add_argument(
            '--no-aiomonitor', dest='aiomonitor', action='store_false', default=True,
            help='disable aiomonitor debugging server')
        self.add_argument(
            '--aiomonitor-host', type=str, default=aiomonitor.MONITOR_HOST,
            help='bind host for aiomonitor/aioconsole [%(default)s]')
        self.add_argument(
            '--aiomonitor-port', type=int, default=aiomonitor.MONITOR_PORT,
            help='port for aiomonitor [%(default)s]')
        self.add_argument(
            '--aioconsole-port', type=int, default=aiomonitor.CONSOLE_PORT,
            help='port for aioconsole [%(default)s]')
