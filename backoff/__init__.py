import asyncio
import time
import random
import traceback
from typing import Callable, Union


VARIABLES = {"MAX_INIT_BACKOFF_SECONDS": 806400.0, "MAX_SLEEP_TIME": 2563488.0}


class MaxRetriesExceeded(Exception):
    """Exception is raised when a backoff has retried too many times."""


class ExponentialBackoff(object):
    def __init__(self, max_retries: int = None, backoff_seconds: Union[int, float] = 1):
        self.tries = 0

        if max_retries is not None:
            if not isinstance(max_retries, int):
                raise TypeError("max_retries must be an integer, not %r" % type(max_retries))
            if max_retries <= 0:
                raise ValueError("max_retries cannot be zero or lower.")
        self.max_tries = max_retries

        if not isinstance(backoff_seconds, (float, int)):
            raise TypeError("backoff_seconds must be an integer or float, not %r" % type(max_retries))
        elif backoff_seconds >= VARIABLES["MAX_INIT_BACKOFF_SECONDS"]:
            raise ValueError("backoff_seconds is too large.")
        elif backoff_seconds <= 0.0:
            raise ValueError("backoff_seconds must be greater than zero.")
        self.backoff_seconds = backoff_seconds

        self.__first_call = True

    def reset(self) -> None:
        """Resets the internal number of iterations to 0.

        This is only really useful if you want to re-start the backoff, without making a new object."""
        self.tries = 0

    def next_sleep_time(self) -> float:
        """
        Calculates how long the next sleep call will last.

        :return: int - how long to sleep, in seconds
        """
        if self.__first_call:
            return 0.0
        return self.backoff_seconds * 2 ** self.tries + random.uniform(0, 1)

    def add_try(self) -> None:
        self.tries += 1
        if self.max_tries is not None and self.tries >= self.max_tries:
            raise MaxRetriesExceeded("Max retries exceeded (attempts: {0.tries}, max: {0.max_tries})".format(self))

    def __iter__(self) -> "ExponentialBackoff":
        return self

    async def __aiter__(self) -> "ExponentialBackoff":
        return self

    def __next__(self) -> int:
        self.add_try()
        sleep_time = self.next_sleep_time()
        time.sleep(sleep_time)
        self.__first_call = False
        return self.tries

    async def __anext__(self) -> int:
        self.add_try()
        sleep_time = self.next_sleep_time()
        await asyncio.sleep(sleep_time)
        self.__first_call = False
        return self.tries


def retry_with_backoff(
    max_retries: int = 10, backoff_seconds: Union[int, float] = 1.0, *, exception_handler: Callable = None
) -> Callable:
    """
    Attach a decorator to a function that will retry a function up to N times with exponential backoff until it succeeds

    :param max_retries: The maximum number of times to retry the call until giving up.
    :param backoff_seconds: How long, in seconds, the initial backoff should last.
    :param exception_handler: A function that will take one argument, type Exception, that is called on error.
    :return: Function (decorator)
    """

    def _default_handler(exception: Exception) -> None:
        traceback.print_exception(type(exception), exception, exception.__traceback__)

    if not isinstance(max_retries, int):
        raise TypeError("max_retries must be an integer, not %r" % type(max_retries))
    if max_retries <= 0:
        raise ValueError("max_retries cannot be less than one.")

    if not isinstance(backoff_seconds, (int, float)):
        raise TypeError("backoff_seconds must be an integer or float, not %r" % type(backoff_seconds))
    if backoff_seconds <= 0.0:
        raise ValueError("backoff_seconds must be greater than zero.")

    if exception_handler is not None and not callable(exception_handler):
        raise TypeError("exception_handler must be a callable function, not %r" % type(exception_handler))
    if asyncio.iscoroutinefunction(exception_handler):
        raise TypeError("exception_handler cannot be an asynchronous function.")

    exception_handler = exception_handler or _default_handler

    def wrapper(function: Callable, *args, **kwargs):
        if asyncio.iscoroutinefunction(function):
            raise TypeError("Unable to execute an asynchronous function.")
        _backoff = ExponentialBackoff(max_retries, backoff_seconds)
        function.backoff_object = _backoff

        def _wrapper():
            # noinspection PyUnresolvedReferences
            for _ in function.backoff_object:
                try:
                    return function(*args, **kwargs)
                except Exception as e:
                    exception_handler(e)  # If this function errors, then we quit the loop.

        return _wrapper

    return wrapper
