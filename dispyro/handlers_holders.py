from collections.abc import Container
from contextlib import suppress
from typing import List, Optional, Type

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
    InlineQueryHandler,
    MessageHandler,
    PollHandler,
    RawUpdateHandler,
    UserStatusHandler,
)
from .processing_context_holder import ProcessingContextHolder
from .types import AnyFilter, Handler, PackedRawUpdate
from .types.contexts import UpdateContext
from .types.signatures import (
    CallbackQueryHandlerCallback,
    ChatMemberUpdatedHandlerCallback,
    ChosenInlineResultHandlerCallback,
    Decorator,
    DeletedMessagesHandlerCallback,
    EditedMessageHandlerCallback,
    InlineQueryHandlerCallback,
    MessageHandlerCallback,
    PollHandlerCallback,
    RawUpdateHandlerCallback,
    UserStatusHandlerCallback,
)
from .utils import InterruptProcessing


class HandlersHolder(ProcessingContextHolder):
    __handler_type__: Type[Handler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(filters=filters)

        self.handlers: List[Handler] = []
        self._router = router

    def register(self, callback, filters: AnyFilter = Filter(), priority: Optional[int] = None):
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

    def __call__(self, filters: Filter = Filter(), priority: Optional[int] = None):
        def decorator(callback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator

    async def feed_update(self, context: UpdateContext, run_logic: RunLogic) -> bool:
        client = context.client
        update = context.update
        deps = context.data

        with suppress(InterruptProcessing):
            for middleware in self.outer_middlewares:
                await middleware.handle(context=context)

            filters_passed = await self.filters(client, update, **deps)

            if not filters_passed:
                for middleware in reversed(self.outer_middlewares):
                    await middleware.handle(context=context)

                return False

            for middleware in self.middlewares:
                await middleware.handle(context=context)

            self._router._triggered = True

            result = False

            handlers = sorted(self.handlers, key=lambda x: x._priority)
            for handler in handlers:
                await handler(
                    client=context.client, update=context.update, **context.data  # pyright: ignore [reportArgumentType]
                )

                if handler._triggered and run_logic in {
                    RunLogic.ONE_RUN_PER_ROUTER,
                    RunLogic.ONE_RUN_PER_EVENT,
                }:
                    result = True
                    break

            # result = any(handler._triggered for handler in handlers)

            # for middleware in reversed(self.middlewares):
            #     await middleware.handle(context=context)

            # for middleware in reversed(self.outer_middlewares):
            #     await middleware.handle(context=context)

            return result

        return False


class CallbackQueryHandlersHolder(HandlersHolder):
    __handler_type__ = CallbackQueryHandler
    handlers: List[CallbackQueryHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: CallbackQueryHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: Optional[int] = None,
    ) -> CallbackQueryHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: AnyFilter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: CallbackQueryHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator


class ChatMemberUpdatedHandlersHolder(HandlersHolder):
    __handler_type__ = ChatMemberUpdatedHandler
    handlers: List[ChatMemberUpdatedHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: ChatMemberUpdatedHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: Optional[int] = None,
    ) -> ChatMemberUpdatedHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: AnyFilter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: ChatMemberUpdatedHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator


class ChosenInlineResultHandlersHolder(HandlersHolder):
    __handler_type__ = ChosenInlineResultHandler
    handlers: List[ChosenInlineResultHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: ChosenInlineResultHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: Optional[int] = None,
    ) -> ChosenInlineResultHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: AnyFilter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: ChosenInlineResultHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator


class DeletedMessagesHandlersHolder(HandlersHolder):
    __handler_type__ = DeletedMessagesHandler
    handlers: List[DeletedMessagesHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: DeletedMessagesHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: Optional[int] = None,
    ) -> DeletedMessagesHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: AnyFilter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: DeletedMessagesHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator


class EditedMessageHandlersHolder(HandlersHolder):
    __handler_type__ = EditedMessageHandler
    handlers: List[EditedMessageHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: EditedMessageHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: Optional[int] = None,
    ) -> EditedMessageHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: AnyFilter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: EditedMessageHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator


class InlineQueryHandlersHolder(HandlersHolder):
    __handler_type__ = InlineQueryHandler
    handlers: List[InlineQueryHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: InlineQueryHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: Optional[int] = None,
    ) -> InlineQueryHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: AnyFilter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: InlineQueryHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator


class MessageHandlersHolder(HandlersHolder):
    __handler_type__ = MessageHandler
    handlers: List[MessageHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: MessageHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: Optional[int] = None,
    ) -> MessageHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: AnyFilter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: MessageHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator


class PollHandlersHolder(HandlersHolder):
    __handler_type__ = PollHandler
    handlers: List[PollHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: PollHandlerCallback,
        filters: AnyFilter = Filter(),
        priority: Optional[int] = None,
    ) -> PollHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: AnyFilter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: PollHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator


class RawUpdateHandlersHolder(HandlersHolder):
    __handler_type__ = RawUpdateHandler
    handlers: List[RawUpdateHandler]

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: RawUpdateHandlerCallback,
        filters: Filter = Filter(),
        priority: Optional[int] = None,
        allowed_updates: Optional[List[Type[core.TLObject]]] = None,
        allowed_update: Optional[Type[core.TLObject]] = None,
    ) -> RawUpdateHandlerCallback:
        if allowed_updates and allowed_update:
            raise ValueError("`allowed_updates` and `allowed_update` are mutually exclusive")

        _allowed_updates: Optional[List[Type[core.TLObject]]] = None

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

            types_filter = Filter(callback=types_filter_callback)  # pyright: ignore [reportArgumentType]
            filters = types_filter & filters

        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(
        self,
        filters: Filter = Filter(),
        priority: Optional[int] = None,
        allowed_updates: Optional[List[Type[core.TLObject]]] = None,
        allowed_update: Optional[Type[core.TLObject]] = None,
    ) -> Decorator:
        def decorator(callback: RawUpdateHandlerCallback) -> RawUpdateHandlerCallback:
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

    def __init__(self, router: "dispyro.Router", filters: Optional[AnyFilter] = None):
        super().__init__(router=router, filters=filters)

    def register(
        self,
        callback: UserStatusHandlerCallback,
        filters: Filter = Filter(),
        priority: Optional[int] = None,
    ) -> UserStatusHandlerCallback:
        return super().register(callback=callback, filters=filters, priority=priority)

    def __call__(self, filters: Filter = Filter(), priority: Optional[int] = None) -> Decorator:
        def decorator(callback: UserStatusHandlerCallback):
            return self.register(callback=callback, filters=filters, priority=priority)

        return decorator
