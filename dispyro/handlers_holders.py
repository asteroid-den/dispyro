from collections.abc import Container
from typing import Callable, List, Optional

from pyrogram import Client, types
from pyrogram.raw import base

import dispyro

from .enums import RunLogic
from .filters import Filter
from .handlers import (
    CallbackQueryHandler,
    ChatMemberUpdatedHandler,
    ChosenInlineResultHandler,
    DeletedMessagesHandler,
    EditedMessageHandler,
    InlineQueryHandler,
    MessageHandler,
    PollHandler,
    RawUpdateHandler,
    UserStatusHandler,
)
from .types import AnyFilter, Callback, Handler, PackedRawUpdate, Update


class HandlersHolder:
    __handler_type__: Handler

    def __init__(self, router: "dispyro.Router", filters: AnyFilter = None):
        self.filters = Filter() & filters if filters else Filter()
        self.handlers: List[Handler] = []
        self._router = router

    def filter(self, filter: AnyFilter) -> None:
        self.filters &= filter

    def register(
        self, callback: Callback, filters: Filter = Filter(), priority: int = None
    ) -> Callback:
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

    def __call__(
        self, filters: Filter = Filter(), priority: int = None
    ) -> Callable[[Callback], Callback]:
        def decorator(callback: Callback) -> Callback:
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: Update, **deps
    ) -> bool:
        filters_passed = await self.filters(client, update, **deps)

        if not filters_passed:
            return False

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
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)


class ChatMemberUpdatedHandlersHolder(HandlersHolder):
    __handler_type__ = ChatMemberUpdatedHandler
    handlers: List[ChatMemberUpdatedHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.ChatMemberUpdated, **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)


class ChosenInlineResultHandlersHolder(HandlersHolder):
    __handler_type__ = ChosenInlineResultHandler
    handlers: List[ChosenInlineResultHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.ChosenInlineResult, **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)


class DeletedMessagesHandlersHolder(HandlersHolder):
    __handler_type__ = DeletedMessagesHandler
    handlers: List[DeletedMessagesHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: List[types.Message], **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)


class EditedMessageHandlersHolder(HandlersHolder):
    __handler_type__ = EditedMessageHandler
    handlers: List[EditedMessageHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.Message, **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)


class InlineQueryHandlersHolder(HandlersHolder):
    __handler_type__ = InlineQueryHandler
    handlers: List[InlineQueryHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.InlineQuery, **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)


class MessageHandlersHolder(HandlersHolder):
    __handler_type__ = MessageHandler
    handlers: List[MessageHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.Message, **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)


class PollHandlersHolder(HandlersHolder):
    __handler_type__ = PollHandler
    handlers: List[PollHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.Poll, **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)


class RawUpdateHandlersHolder(HandlersHolder):
    __handler_type__ = RawUpdateHandler
    handlers: List[RawUpdateHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: PackedRawUpdate, **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)

    def register(
        self,
        callback: Callback,
        filters: Filter = Filter(),
        priority: int = None,
        allowed_updates: List[type[base.Update]] = None,
        allowed_update: type[base.Update] = None,
    ) -> Callback:
        if allowed_updates and allowed_update:
            raise ValueError("`allowed_updates` and `allowed_update` are mutually exclusive")

        _allowed_updates: Optional[List[type[base.Update]]] = None

        if allowed_update is not None:
            if isinstance(allowed_update, Container):
                raise ValueError(
                    "list (or other container) should be passed as `allowed_updates`, not as `allowed_update`"
                )

            _allowed_updates = [allowed_update]

        elif allowed_updates is not None:
            if not isinstance(allowed_updates, Container):
                raise TypeError("`allowed_updates` object should have `__contains__` defined")

            _allowed_updates = allowed_updates

        if _allowed_updates is not None:

            async def types_filter_callback(_, update: PackedRawUpdate) -> bool:
                return type(update.update) in _allowed_updates

            types_filter = Filter(callback=types_filter_callback)
            filters = types_filter & filters

        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(
        self,
        filters: Filter = Filter(),
        priority: int = None,
        allowed_updates: List[type[base.Update]] = None,
        allowed_update: type[base.Update] = None,
    ) -> Callable[[Callback], Callback]:
        def decorator(callback: Callback) -> Callback:
            return self.register(
                callback=callback,
                filters=filters,
                priority=priority,
                allowed_updates=allowed_updates,
                allowed_update=allowed_update,
            )

        return decorator


class UserStatusHandlersHolder(HandlersHolder):
    __handler_type__ = UserStatusHandler
    handlers: List[UserStatusHandler]

    async def feed_update(
        self, client: Client, run_logic: RunLogic, update: types.User, **deps
    ) -> bool:
        return await super().feed_update(client=client, run_logic=run_logic, update=update, **deps)
