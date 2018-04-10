"""Utilities for interfacing between trollius and tornado"""

import trollius
import tornado.concurrent


def to_tornado_future(trollius_future, loop=None):
    """Modified version of :func:`tornado.platform.asyncio.to_tornado_future`
    that is a bit more robust: it allows taking a coroutine rather than a
    future, it passes through error tracebacks, and if a future is cancelled it
    properly propagates the CancelledError.
    """
    f = trollius.ensure_future(trollius_future, loop=loop)
    tf = tornado.concurrent.Future()

    def copy(future):
        assert future is f
        if f.cancelled():
            tf.set_exception(trollius.CancelledError())
        elif hasattr(f, '_get_exception_tb') and f._get_exception_tb() is not None:
            # Note: f.exception() clears the traceback, so must retrieve it first
            tb = f._get_exception_tb()
            exc = f.exception()
            tf.set_exc_info((type(exc), exc, tb))
        elif f.exception() is not None:
            tf.set_exception(f.exception())
        else:
            tf.set_result(f.result())
    f.add_done_callback(copy)
    return tf
