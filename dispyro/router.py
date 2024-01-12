from functools import cached_property
from typing import Dict, List

from pyrogram import Client, handlers
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
from .types import Update


class Router:
    """Router class used to put subset of handlers together.

    To put things to work, must be attached to `Dispatcher`.
    """

    def __init__(self, name: str = None):
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
    def handlers_correlation(self) -> Dict[PyrogramHandler, HandlersHolder]:
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

    def cleanup(self) -> None:
        self._triggered = False

        for handler in self.all_handlers:
            handler._triggered = False

    async def feed_update(
        self,
        client: Client,
        dispatcher: "dispyro.Dispatcher",
        update: Update,
        handler_type: PyrogramHandler,
        **deps,
    ) -> bool:
        run_logic = dispatcher._run_logic

        handlers_holder = self.handlers_correlation[handler_type]

        result = await handlers_holder.feed_update(
            client=client, run_logic=run_logic, update=update, **deps
        )

        return result
