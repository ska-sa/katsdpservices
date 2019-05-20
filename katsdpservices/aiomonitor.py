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
