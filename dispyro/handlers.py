# This file defines custom handlers definitions that is used instead of
# original Pyrogram handlers. Unlike original handlers, customs are DI-friendly,
# providing ability to use dependency injection with ease.
#
# Groups were removed because of changed processing logic (actual handlers
# distribution instead of formal split by groups, which made groups useless).
# Instead of them, new attribute added: `priority`, which affects on handlers
# order inside of specific router. Lower number means higher priority (highest
# priority is 1), handlers with same priority arranged corresponding to order
# in which they were registered. By default, all registered handlers priority
# is set to 1. You can customize this behaviour by providing your own
# `priority_factory`. This function must take 2 arguments
# (handler itself and `router` that registering this handler) and return
# positive `int`.

from typing import Callable

from pyrogram import Client, types

import dispyro

from .signatures import (
    CallbackQueryHandlerCallback,
    ChatMemberUpdatedHandlerCallback,
    ChosenInlineResultHandlerCallback,
    EditedMessageHandlerCallback,
    InlineQueryHandlerCallback,
    MessageHandlerCallback,
    PollHandlerCallback,
)
from .union_types import AnyFilter, Callback, Update
from .utils import safe_call

PriorityFactory = Callable[["Handler", "dispyro.Router"], int]


class Handler:
    def _default_priority_factory(self, _) -> int:
        return 1

    _priority_factory: PriorityFactory = _default_priority_factory

    @classmethod
    def set_priority_factory(cls, priority_factory: PriorityFactory) -> None:
        cls._priority_factory = priority_factory

    def __init__(
        self,
        *,
        callback: Callback,
        router: "dispyro.Router",
        name: str = None,
        priority: int = None,
        filters: AnyFilter = dispyro.filters.Filter(),
    ):
        if priority is not None:
            self._priority = priority
        else:
            self._priority = self._priority_factory(router)

        self._name = name or "unnamed_handler"
        self.callback: Callback = safe_call(callable=callback)
        self._router = router
        self._filters: dispyro.filters.Filter = dispyro.filters.Filter() & filters

        # This field indicates whether handler was called during handling current
        # update. Defaults to `False`. Set to `False` on cleanup (after finishing
        # update processing).
        self._triggered: bool = False

    async def __call__(
        self,
        *,
        client: Client,
        update: Update,
        **deps,
    ) -> None:
        filters_passed = await self._filters(client=client, update=update, **deps)

        if not filters_passed:
            return

        await self.callback(client, update, **deps)
        self._triggered = True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} `{self._name}`"


class CallbackQueryHandler(Handler):
    callback: CallbackQueryHandlerCallback

    def __init__(
        self,
        *,
        callback: CallbackQueryHandlerCallback,
        router: "dispyro.Router",
        name: str = None,
        priority: int = None,
        filters: AnyFilter = dispyro.filters.Filter(),
    ):
        super().__init__(
            callback=callback,
            router=router,
            name=name,
            priority=priority,
            filters=filters,
        )

    async def __call__(
        self,
        *,
        client: Client,
        update: types.CallbackQuery,
        **deps,
    ) -> None:
        await super().__call__(client=client, update=update, **deps)


class ChatMemberUpdatedHandler(Handler):
    callback: ChatMemberUpdatedHandlerCallback

    def __init__(
        self,
        *,
        callback: ChatMemberUpdatedHandlerCallback,
        router: "dispyro.Router",
        name: str = None,
        priority: int = None,
        filters: AnyFilter = dispyro.filters.Filter(),
    ):
        super().__init__(
            callback=callback,
            router=router,
            name=name,
            priority=priority,
            filters=filters,
        )

    async def __call__(
        self,
        *,
        client: Client,
        update: types.ChatMemberUpdated,
        **deps,
    ) -> None:
        await super().__call__(client=client, update=update, **deps)


class ChosenInlineResultHandler(Handler):
    callback: ChosenInlineResultHandlerCallback

    def __init__(
        self,
        *,
        callback: ChosenInlineResultHandlerCallback,
        router: "dispyro.Router",
        name: str = None,
        priority: int = None,
        filters: AnyFilter = dispyro.filters.Filter(),
    ):
        super().__init__(
            callback=callback,
            router=router,
            name=name,
            priority=priority,
            filters=filters,
        )

    async def __call__(
        self,
        *,
        client: Client,
        update: types.ChosenInlineResult,
        **deps,
    ) -> None:
        await super().__call__(client=client, update=update, **deps)


class EditedMessageHandler(Handler):
    callback: EditedMessageHandlerCallback

    def __init__(
        self,
        *,
        callback: EditedMessageHandlerCallback,
        router: "dispyro.Router",
        name: str = None,
        priority: int = None,
        filters: AnyFilter = dispyro.filters.Filter(),
    ):
        super().__init__(
            callback=callback,
            router=router,
            name=name,
            priority=priority,
            filters=filters,
        )

    async def __call__(
        self,
        *,
        client: Client,
        update: types.Message,
        **deps,
    ) -> None:
        await super().__call__(client=client, update=update, **deps)


class InlineQueryHandler(Handler):
    callback: InlineQueryHandlerCallback

    def __init__(
        self,
        *,
        callback: InlineQueryHandlerCallback,
        router: "dispyro.Router",
        name: str = None,
        priority: int = None,
        filters: AnyFilter = dispyro.filters.Filter(),
    ):
        super().__init__(
            callback=callback,
            router=router,
            name=name,
            priority=priority,
            filters=filters,
        )

    async def __call__(
        self,
        *,
        client: Client,
        update: types.InlineQuery,
        **deps,
    ) -> None:
        await super().__call__(client=client, update=update, **deps)


class MessageHandler(Handler):
    callback: MessageHandlerCallback

    def __init__(
        self,
        *,
        callback: MessageHandlerCallback,
        router: "dispyro.Router",
        name: str = None,
        priority: int = None,
        filters: AnyFilter = dispyro.filters.Filter(),
    ):
        super().__init__(
            callback=callback,
            router=router,
            name=name,
            priority=priority,
            filters=filters,
        )

    async def __call__(
        self,
        *,
        client: Client,
        update: types.Message,
        **deps,
    ) -> None:
        await super().__call__(client=client, update=update, **deps)


class PollHandler(Handler):
    callback: PollHandlerCallback

    def __init__(
        self,
        *,
        callback: PollHandlerCallback,
        router: "dispyro.Router",
        name: str = None,
        priority: int = None,
        filters: AnyFilter = dispyro.filters.Filter(),
    ):
        super().__init__(
            callback=callback,
            router=router,
            name=name,
            priority=priority,
            filters=filters,
        )

    async def __call__(
        self,
        *,
        client: Client,
        update: types.Poll,
        **deps,
    ) -> None:
        await super().__call__(client=client, update=update, **deps)
