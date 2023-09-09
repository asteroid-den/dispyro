from pyrogram import Client
from pyrogram.filters import Filter as PyrogramFilter

from .signatures import FilterCallback
from .union_types import AnyFilter, Update
from .utils import safe_call


class Filter:
    """Custom version of `Filter` type, which supports DI. This filters can be
    combined with default pyrogram filters.
    """

    async def _default_callback(self, client: Client, update: Update):
        return True

    def __init__(self, callback: FilterCallback = None):
        self._unwrapped_callback = callback
        self._callback: FilterCallback = safe_call(callback or self._default_callback)

    async def __call__(self, client: Client, update: Update, **deps) -> bool:
        return await self._callback(client, update, **deps)

    def __invert__(self) -> "InvertedFilter":
        return InvertedFilter(callback=self._unwrapped_callback)

    def __and__(self, other: AnyFilter) -> "AndFilter":
        return AndFilter(left=self, right=other)

    def __or__(self, other: AnyFilter) -> "OrFilter":
        return OrFilter(left=self, right=other)


class InvertedFilter(Filter):
    async def __call__(self, client: Client, update: Update, **deps) -> bool:
        return not await super().__call__(client, update, **deps)


class AndFilter(Filter):
    def __init__(self, left: AnyFilter, right: AnyFilter):
        if isinstance(left, PyrogramFilter):
            left = safe_call(callable=left)

        if isinstance(right, PyrogramFilter):
            right = safe_call(callable=right)

        self._left: AnyFilter = left
        self._right: AnyFilter = right

    async def __call__(self, client: Client, update: Update, **deps) -> bool:
        left_value = await self._left(client, update, **deps)

        if not left_value:
            return False

        right_value = await self._right(client, update, **deps)

        return left_value and right_value


class OrFilter(Filter):
    def __init__(self, left: AnyFilter, right: AnyFilter):
        if isinstance(left, PyrogramFilter):
            left = safe_call(callable=left)

        if isinstance(right, PyrogramFilter):
            right = safe_call(callable=right)

        self._left: AnyFilter = left
        self._right: AnyFilter = right

    async def __call__(self, client: Client, update: Update, **deps) -> bool:
        left_value = await self._left(client, update, **deps)

        if left_value:
            return True

        right_value = await self._right(client, update, **deps)

        return left_value or right_value
