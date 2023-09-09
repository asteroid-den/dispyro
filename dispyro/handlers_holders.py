from typing import Callable, List

from pyrogram import Client, types

import dispyro

from .enums import RunLogic
from .filters import Filter
from .handlers import (
    CallbackQueryHandler,
    ChatMemberUpdatedHandler,
    ChosenInlineResultHandler,
    EditedMessageHandler,
    InlineQueryHandler,
    MessageHandler,
    PollHandler,
)
from .union_types import AnyFilter, Callback, Handler, Update


class HandlersHolder:
    __handler_type__: Handler

    def __init__(self, router: "dispyro.Router", filters: AnyFilter = None):
        self.filters = Filter() & filters if filters else Filter()
        self.handlers: List[Handler] = []
        self._router = router

    def filter(self, filter: AnyFilter) -> None:
        self.filters &= filter

    def __call__(
        self, filters: Filter = Filter(), priority: int = None
    ) -> Callable[[Callback], Callback]:
        def decorator(callback: Callback) -> Callback:
            nonlocal filters

            handler_type = self.__handler_type__
            self.handlers.append(
                handler_type(
                    callback=callback,
                    router=self._router,
                    priority=priority,
                    filters=filters,
                )
            )

            return callback

        return decorator

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: Update, **deps
    ) -> bool:
        filters_passed = await self.filters(client=client, update=update, **deps)

        if not filters_passed:
            return

        self._router._triggered = True

        handlers = sorted(self.handlers, key=lambda x: x._priority)
        for handler in handlers:
            await handler(client=client, update=update, **deps)

            if handler._triggered and run_logic in {
                RunLogic.ONE_RUN_PER_ROUTER,
                RunLogic.ONE_RUN_PER_EVENT,
            }:
                return True

        return any(handler._triggered for handler in handlers)

class CallbackQueryHandlersHolder(HandlersHolder):
    __handler_type__ = CallbackQueryHandler
    handlers: List[CallbackQueryHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.CallbackQuery, **deps
    ) -> bool:
        return await super().feed_update(
            client=client, run_logic=run_logic, update=update, **deps
        )


class ChatMemberUpdatedHandlersHolder(HandlersHolder):
    __handler_type__ = ChatMemberUpdatedHandler
    handlers: List[ChatMemberUpdatedHandler]

    async def feed_update(
        self,
        client: Client,
        run_logic: RunLogic,
        update: types.ChatMemberUpdated,
        **deps
    ) -> bool:
        return await super().feed_update(
            client=client, run_logic=run_logic, update=update, **deps
        )


class ChosenInlineResultHandlersHolder(HandlersHolder):
    __handler_type__ = ChosenInlineResultHandler
    handlers: List[ChosenInlineResultHandler]

    async def feed_update(
        self,
        client: Client,
        run_logic: RunLogic,
        update: types.ChosenInlineResult,
        **deps
    ) -> bool:
        return await super().feed_update(
            client=client, run_logic=run_logic, update=update, **deps
        )


class EditedMessageHandlersHolder(HandlersHolder):
    __handler_type__ = EditedMessageHandler
    handlers: List[EditedMessageHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.Message, **deps
    ) -> bool:
        return await super().feed_update(
            client=client, run_logic=run_logic, update=update, **deps
        )


class InlineQueryHandlersHolder(HandlersHolder):
    __handler_type__ = InlineQueryHandler
    handlers: List[InlineQueryHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.InlineQuery, **deps
    ) -> bool:
        return await super().feed_update(
            client=client, run_logic=run_logic, update=update, **deps
        )


class MessageHandlersHolder(HandlersHolder):
    __handler_type__ = MessageHandler
    handlers: List[MessageHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.Message, **deps
    ) -> bool:
        return await super().feed_update(
            client=client, run_logic=run_logic, update=update, **deps
        )


class PollHandlersHolder(HandlersHolder):
    __handler_type__ = PollHandler
    handlers: List[PollHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.Poll, **deps
    ) -> bool:
        return await super().feed_update(
            client=client, run_logic=run_logic, update=update, **deps
        )
