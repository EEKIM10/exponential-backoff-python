# Exponential Backoff!
Simple exponential backoff python implementation to ensure your programs never have to deal with the horrible loops again!

## Installation
```shell
$ pip install another-exponential-backoff
# OR
$ pip install git+https://github.com/dragdev-studios/exponential-backoff-python
```

## Usage
```python
import random
import aiohttp
import backoff
# OR
# from backoff import ExponentialBackoff, MaxRetriesExceeded, retry_with_backoff

# Please note that the retry_with_backoff decorator is non-coroutine only.
@backoff.retry_with_backoff(max_retries=10, backoff_seconds=1)
def get_bank_balance():
    if random.randint(1, 10) == 7:
        print("You won the lottery! You now have £7,000,000!")
        return  # this won't cause the function to restart
    raise ValueError("You have no money in the bank.")  # raising an error, causing the function to exit, will.

async def get_page(url):
    backoff_handler = backoff.ExponentialBackoff(30)
    session = aiohttp.ClientSession()
    print("Attempting to download", url)
    try:
        async for attempt in backoff_handler:
            page = await session.get(url)
            if page.status != 200:
                print(f"Attempt #{attempt} failed. Retrying.")
            else:
                break
    except backoff.MaxRetriesExceeded:
        print("Failed to fetch page too many times. Try again later.")
    else:
        print("Super secret content:", page)
```

## Contributing
If you have a contribution that you believe would help the project, please ensure you do both of the following,
before opening a pull request:

1. Run `black backoff -l 120`.
2. Run `pytest` (if any of these fail, fix and re-commit)

Any pulls with failing tests will not be considered until the author fixes those problems.
