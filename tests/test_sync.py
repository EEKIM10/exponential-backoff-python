import random

import pytest
from backoff import ExponentialBackoff, retry_with_backoff, MaxRetriesExceeded

RAISABLE_ERRORS = (
    ValueError("Preset test exception"),
    TypeError("Preset test exception"),
    IndexError("Preset test exception"),
    AttributeError("Preset test exception")
)


def sync_may_raise():
    if random.randint(0, 5) == 3:
        raise random.choice(RAISABLE_ERRORS)
    return True


async def async_may_raise():
    sync_may_raise()  # im lazy


def should_not_run():
    raise AssertionError("Function ran that should not.")


@pytest.mark.parametrize(
    ("max_retries", "backoff_seconds", "expected_exceptions"),
    (
        (1, 10.0, []),
        ("1", 10, (TypeError,)),
        (-1, 10, (ValueError,)),
        (1, -1, (ValueError,)),
        (1, float("inf"), (ValueError,)),
        (1.0, 10, (TypeError,))
    )
)
def test_class_construction(max_retries, backoff_seconds, expected_exceptions):
    if not bool(expected_exceptions):
        x = ExponentialBackoff(max_retries, backoff_seconds)
        assert x.max_tries == max_retries
        assert x.tries == 0
        assert x.backoff_seconds == backoff_seconds
    else:
        with pytest.raises(expected_exceptions):
            ExponentialBackoff(max_retries, backoff_seconds)


def test_max_tries():
    x = ExponentialBackoff(50, 1)
    for i in range(100):
        if i >= 49:
            with pytest.raises(MaxRetriesExceeded):
                x.add_try()
        else:
            x.add_try()


def test_iter():
    x = ExponentialBackoff(None, 0.5)
    for y in x:
        print("Sleeping for", y, "seconds.")
        if x.tries == 3:
            break


@pytest.mark.parametrize(
    (
        "max_retries",
        "backoff_seconds",
        "exception_handler",
        "expected_exceptions"
    ),
    (
        (10, 1, lambda e: print(e), []),
        ("10", 1, lambda e: print(e), (TypeError,)),
        (-10, 1, lambda e: print(e), (ValueError,)),
        (10, 0.1, lambda e: print(e), []),
        (10, -0.6, lambda e: print(e), (ValueError,)),
        (10, 1, None, []),
        (10, 1, False, (TypeError,)),
        (10, 1, async_may_raise, (TypeError,)),
        (None, None, None, (TypeError, ValueError))
    )
)
def test_decorator(max_retries, backoff_seconds, exception_handler, expected_exceptions):
    if not bool(expected_exceptions):
        retry_with_backoff(max_retries, backoff_seconds, exception_handler=exception_handler)(should_not_run)
    else:
        with pytest.raises(expected_exceptions):
            retry_with_backoff(max_retries, backoff_seconds, exception_handler=exception_handler)(should_not_run)

