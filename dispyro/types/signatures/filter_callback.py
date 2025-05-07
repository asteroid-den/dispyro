from typing import Callable, Awaitable

FilterCallback = Callable[..., Awaitable[bool]]