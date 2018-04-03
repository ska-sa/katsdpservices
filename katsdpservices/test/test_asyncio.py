"""Tests for :mod:`katsdpservices.asyncio`"""

import sys
import traceback
import functools
import contextlib
import trollius
from trollius import From
from nose.tools import assert_equal, assert_raises, assert_true, assert_is_not_none
from ..asyncio import to_tornado_future


class MyException(Exception):
    """Exception that just needs to be different to library-generated exceptions"""


@trollius.coroutine
def successful():
    return 'successful'


@trollius.coroutine
def never_return(loop):
    yield From(trollius.Future(loop=loop))


@trollius.coroutine
def exception_generator():
    raise MyException('my exception')


def run_with_event_loop(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = trollius.new_event_loop()
        with contextlib.closing(loop):
            args2 = args + (loop,)
            loop.run_until_complete(func(*args2, **kwargs))
    return wrapper


@run_with_event_loop
def test_to_tornado_future_success(loop):
    f = trollius.ensure_future(successful(), loop=loop)
    tf = to_tornado_future(f)
    yield From(trollius.wait([f], loop=loop))
    assert_equal('successful', tf.result())


@run_with_event_loop
def test_to_tornado_future_cancelled(loop):
    f = trollius.ensure_future(never_return(loop), loop=loop)
    tf = to_tornado_future(f)
    f.cancel()
    yield From(trollius.wait([f], loop=loop))
    with assert_raises(trollius.CancelledError):
        tf.result()


@run_with_event_loop
def test_to_tornado_future_exception(loop):
    f = trollius.ensure_future(exception_generator(), loop=loop)
    tf = to_tornado_future(f)
    yield From(trollius.wait([f], loop=loop))
    tb = None
    with assert_raises(MyException):
        try:
            tf.result()
        except Exception:
            tb = traceback.extract_tb(sys.exc_info()[2])
            raise
    assert_is_not_none(tb)
    found = False
    for frame in tb:
        if frame[2] == 'exception_generator':
            found = True
    assert_true(found, 'traceback did not contain our function')


@run_with_event_loop
def test_to_tornado_future_exception_no_tb(loop):
    f = trollius.Future(loop=loop)
    tf = to_tornado_future(f)
    f.set_exception(MyException('exception with no traceback'))
    yield From(trollius.wait([f], loop=loop))
    print(f._get_exception_tb())
    with assert_raises(MyException):
        tf.result()
