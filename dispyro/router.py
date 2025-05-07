from functools import cached_property
from typing import Dict, List, Optional, Type

from pyrogram import handlers
from pyrogram.handlers.handler import Handler as PyrogramHandler

import dispyro

from .handlers import Handler
from .handlers_holders import (
    CallbackQueryHandlersHolder,
    ChatMemberUpdatedHandlersHolder,
    ChosenInlineResultHandlersHolder,
    DeletedMessagesHandlersHolder,
    EditedMessageHandlersHolder,
    HandlersHolder,
    InlineQueryHandlersHolder,
    MessageHandlersHolder,
    PollHandlersHolder,
    RawUpdateHandlersHolder,
    UserStatusHandlersHolder,
)
from .types.contexts import UpdateContext


class Router:
    """Router class used to put subset of handlers together.

    To put things to work, must be attached to `Dispatcher`.
    """

    def __init__(self, name: Optional[str] = None):
        self._name = name or "unnamed_router"

        self.callback_query = CallbackQueryHandlersHolder(router=self)
        self.chat_member_updated = ChatMemberUpdatedHandlersHolder(router=self)
        self.chosen_inline_result = ChosenInlineResultHandlersHolder(router=self)
        self.deleted_messages = DeletedMessagesHandlersHolder(router=self)
        self.edited_message = EditedMessageHandlersHolder(router=self)
        self.inline_query = InlineQueryHandlersHolder(router=self)
        self.message = MessageHandlersHolder(router=self)
        self.poll = PollHandlersHolder(router=self)
        self.raw_update = RawUpdateHandlersHolder(router=self)
        self.user_status = UserStatusHandlersHolder(router=self)

        self._triggered: bool = False
        self._sub_routers: List["Router"] = []
        self._parent_router: Optional["Router"] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} `{self._name}`"

    @property
    def all_handlers(self) -> List[Handler]:
        return [
            *self.callback_query.handlers,
            *self.chat_member_updated.handlers,
            *self.chosen_inline_result.handlers,
            *self.deleted_messages.handlers,
            *self.edited_message.handlers,
            *self.inline_query.handlers,
            *self.message.handlers,
            *self.poll.handlers,
            *self.raw_update.handlers,
            *self.user_status.handlers,
        ]

    @cached_property
    def handlers_correlation(self) -> Dict[Type[PyrogramHandler], HandlersHolder]:
        return {
            handlers.CallbackQueryHandler: self.callback_query,
            handlers.ChatMemberUpdatedHandler: self.chat_member_updated,
            handlers.ChosenInlineResultHandler: self.chosen_inline_result,
            handlers.DeletedMessagesHandler: self.deleted_messages,
            handlers.EditedMessageHandler: self.edited_message,
            handlers.InlineQueryHandler: self.inline_query,
            handlers.MessageHandler: self.message,
            handlers.PollHandler: self.poll,
            handlers.RawUpdateHandler: self.raw_update,
            handlers.UserStatusHandler: self.user_status,
        }

    def add_routers(self, *routers: "Router") -> None:
        for router in routers:
            self.add_router(router=router)

    def add_router(self, router: "Router") -> None:
        if router._parent_router is not None:
            raise ValueError("Router already has a parent")

        while True:
            if router._parent_router is None:
                break

            parent = router._parent_router

            if parent is self:
                raise RecursionError("Circular reference detected")

        parent = self._parent_router
        while True:
            if parent is None:
                break

            elif parent is router:
                raise RecursionError("Circular reference detected")

            parent = parent._parent_router

        if self in router._sub_routers:
            raise RecursionError("Circular reference detected")

        if self is router:
            raise RecursionError("Circular reference detected")

        router._parent_router = self
        self._sub_routers.append(router)

    def cleanup(self) -> None:
        self._triggered = False

        for handler in self.all_handlers:
            handler._triggered = False

    async def feed_update(
        self,
        context: UpdateContext,
        dispatcher: "dispyro.Dispatcher",
        handler_type: Type[PyrogramHandler],
    ) -> bool:
        run_logic = dispatcher._run_logic

        handlers_holder = self.handlers_correlation[handler_type]

        result = await handlers_holder.feed_update(context=context, run_logic=run_logic)

        if not result and self._sub_routers:
            for sub_router in self._sub_routers:
                result = await sub_router.feed_update(context=context, dispatcher=dispatcher, handler_type=handler_type)

                if result:
                    break

        for middleware in reversed(handlers_holder.middlewares):
            await middleware.handle(context=context)

        for middleware in reversed(handlers_holder.outer_middlewares):
            await middleware.handle(context=context)

        return result
