"""Utilities to simplify starting aiomonitor"""

from __future__ import print_function, division, absolute_import


class _DummyContext(object):
    """Context manager that does nothing"""
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def start_aiomonitor(loop, args, locals):
    """Optionally create and start aiomonitor, depending on command-line arguments.

    The return value should be used as a context manager e.g.::

        with start_aiomonitor(loop, args, locals=locals()):
            loop.run_until_complete(main())

    If ``--aiomonitor`` is not passed on the command line, it does not start
    aiomonitor, although the package must still be present.

    Parameters
    ----------
    loop : :class:`asyncio.AbstractEventLoop`
        Event loop to pass to the server
    args : :class:`argparse.Namespace`
        Command-line arguments, returned from a :class:`katsdpservices.ArgumentParser`
        created with ``aiomonitor=True``.
    locals : dict, optional
        Local variables, made available in aioconsole
    """
    import aiomonitor

    if not args.aiomonitor:
        return _DummyContext()
    else:
        return aiomonitor.start_monitor(
            loop=loop,
            host=args.aiomonitor_host,
            port=args.aiomonitor_port,
            console_port=args.aioconsole_port,
            locals=locals)


def add_aiomonitor_arguments(parser):
    """Add a set of arguments for controlling aiomonitor.

    See :func:`.start_aiomonitor` for details.

    Parameters
    ----------
    parser : :class:`argparse.ArgumentParser`
        Parser to which arguments will be added.
    """
    import aiomonitor
    parser.add_argument(
        '--aiomonitor', action='store_true', default=False,
        help='run aiomonitor debugging server')
    parser.add_argument(
        '--aiomonitor-host', type=str, default=aiomonitor.MONITOR_HOST,
        help='bind host for aiomonitor/aioconsole [%(default)s]')
    parser.add_argument(
        '--aiomonitor-port', type=int, default=aiomonitor.MONITOR_PORT,
        help='port for aiomonitor [%(default)s]')
    parser.add_argument(
        '--aioconsole-port', type=int, default=aiomonitor.CONSOLE_PORT,
        help='port for aioconsole [%(default)s]')
