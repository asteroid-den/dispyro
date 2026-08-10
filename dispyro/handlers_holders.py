from __future__ import annotations

from collections.abc import Callable, Container
from contextlib import suppress
from typing import Generic, TypeVar

from pyrogram.client import Client
from pyrogram.raw import core

import dispyro

from .enums import RunLogic
from .filters import Filter
from .handlers import (
    CallbackQueryHandler,
    ChatMemberUpdatedHandler,
    ChosenInlineResultHandler,
    DeletedMessagesHandler,
    EditedMessageHandler,
    Handler,
    InlineQueryHandler,
    MessageHandler,
    PollHandler,
    RawUpdateHandler,
    UserStatusHandler,
)
from .processing_context_holder import ProcessingContextHolder
from .types import AnyFilter, Callback, PackedRawUpdate
from .types.contexts import UpdateContext
from .types.signatures import (
    CallbackQueryHandlerCallback,
    ChatMemberUpdatedHandlerCallback,
    ChosenInlineResultHandlerCallback,
    DeletedMessagesHandlerCallback,
    EditedMessageHandlerCallback,
    InlineQueryHandlerCallback,
    MessageHandlerCallback,
    PollHandlerCallback,
    RawUpdateHandlerCallback,
    UserStatusHandlerCallback,
)
from .utils import InterruptProcessing

HandlerCallbackT = TypeVar("HandlerCallbackT", bound=Callback)


class HandlersHolder(ProcessingContextHolder, Generic[HandlerCallbackT]):
    __handler_type__: type[Handler]  # pyright: ignore [reportMissingTypeArgument]

    def __init__(self, router: dispyro.Router, filters: AnyFilter | None = None) -> None:
        super().__init__(filters=filters)
        self.handlers: list[Handler] = []  # pyright: ignore [reportMissingTypeArgument]
        self._router = router

    def register(
        self,
        callback: HandlerCallbackT,
        filters: AnyFilter = Filter(),
        priority: int | None = None,
    ) -> HandlerCallbackT:
        handler = self.__handler_type__(
            callback=callback,
            router=self._router,
            priority=priority,
            filters=filters,
        )
        self.handlers.append(handler)
        return callback

    def __call__(
        self,
        filters: AnyFilter = Filter(),
        priority: int | None = None,
    ) -> Callable[[HandlerCallbackT], HandlerCallbackT]:
        def decorator(callback: HandlerCallbackT) -> HandlerCallbackT:
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator

    async def feed_update(self, context: UpdateContext, run_logic: RunLogic) -> bool:
        with suppress(InterruptProcessing):
            for middleware in self.outer_middlewares:
                await middleware.handle(context=context)

            filters_passed = await self.filters(context=context)

            if not filters_passed:
                return False

            for middleware in self.middlewares:
                await middleware.handle(context=context)

            context.router_triggered = True

            result = False

            handlers = sorted(self.handlers, key=lambda x: x._priority)
            for handler in handlers:
                triggered = await handler(context=context)

                if triggered and run_logic in {
                    RunLogic.ONE_RUN_PER_ROUTER,
                    RunLogic.ONE_RUN_PER_EVENT,
                }:
                    context.handler_triggered = True
                    result = True
                    break

            return result

        return False


class CallbackQueryHandlersHolder(HandlersHolder[CallbackQueryHandlerCallback]):
    __handler_type__ = CallbackQueryHandler


class ChatMemberUpdatedHandlersHolder(HandlersHolder[ChatMemberUpdatedHandlerCallback]):
    __handler_type__ = ChatMemberUpdatedHandler


class ChosenInlineResultHandlersHolder(HandlersHolder[ChosenInlineResultHandlerCallback]):
    __handler_type__ = ChosenInlineResultHandler


class DeletedMessagesHandlersHolder(HandlersHolder[DeletedMessagesHandlerCallback]):
    __handler_type__ = DeletedMessagesHandler


class EditedMessageHandlersHolder(HandlersHolder[EditedMessageHandlerCallback]):
    __handler_type__ = EditedMessageHandler


class InlineQueryHandlersHolder(HandlersHolder[InlineQueryHandlerCallback]):
    __handler_type__ = InlineQueryHandler


class MessageHandlersHolder(HandlersHolder[MessageHandlerCallback]):
    __handler_type__ = MessageHandler


class PollHandlersHolder(HandlersHolder[PollHandlerCallback]):
    __handler_type__ = PollHandler


class RawUpdateHandlersHolder(HandlersHolder[RawUpdateHandlerCallback]):
    __handler_type__ = RawUpdateHandler

    def register(
        self,
        callback: RawUpdateHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: int | None = None,
        allowed_updates: list[type[core.TLObject]] | None = None,
        allowed_update: type[core.TLObject] | None = None,
    ) -> RawUpdateHandlerCallback:
        if allowed_updates and allowed_update:
            raise ValueError("`allowed_updates` and `allowed_update` are mutually exclusive")

        _allowed_updates: list[type[core.TLObject]] | None = None

        if allowed_update is not None:
            if isinstance(allowed_update, Container):
                raise ValueError(
                    "list (or other container) should be passed as `allowed_updates`, not as `allowed_update`",
                )

            _allowed_updates = [allowed_update]

        elif allowed_updates is not None:
            if not isinstance(allowed_updates, Container):
                raise TypeError("`allowed_updates` object should have `__contains__` defined")

            _allowed_updates = allowed_updates

        if _allowed_updates is not None:

            async def types_filter_callback(_: Client, update: PackedRawUpdate) -> bool:
                return type(update.update) in _allowed_updates

            types_filter = Filter(callback=types_filter_callback)  # pyright: ignore [reportArgumentType]
            filters = types_filter & filters

        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(
        self,
        filters: AnyFilter = Filter(),
        priority: int | None = None,
        allowed_updates: list[type[core.TLObject]] | None = None,
        allowed_update: type[core.TLObject] | None = None,
    ) -> Callable[[RawUpdateHandlerCallback], RawUpdateHandlerCallback]:
        def decorator(callback: RawUpdateHandlerCallback) -> RawUpdateHandlerCallback:
            return self.register(
                callback=callback,
                filters=filters,
                priority=priority,
                allowed_updates=allowed_updates,
                allowed_update=allowed_update,
            )

        return decorator


class UserStatusHandlersHolder(HandlersHolder[UserStatusHandlerCallback]):
    __handler_type__ = UserStatusHandler
