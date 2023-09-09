from typing import Protocol

from pyrogram import Client

import dispyro


class FilterCallback(Protocol):
    """Signature class for filters callback with DI support."""

    async def __call__(
        self, client: Client, update: "dispyro.union_types.Update", **deps
    ) -> bool:
        ...
