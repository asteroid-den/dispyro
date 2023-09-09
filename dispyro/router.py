from typing import List, TypeVar, cast

from pyrogram import Client, types

import dispyro

from .handlers import Handler
from .handlers_holders import (
    CallbackQueryHandlersHolder,
    ChatMemberUpdatedHandlersHolder,
    ChosenInlineResultHandlersHolder,
    EditedMessageHandlersHolder,
    InlineQueryHandlersHolder,
    MessageHandlersHolder,
    PollHandlersHolder,
)
from .union_types import Update

ExpectedCondition = TypeVar("ExpectedCondition", bound="dispyro.ExpectedCondition")


class Router:
    """Router class used to put subset of handlers together.

    To put things to work, must be attached to `Dispatcher`.
    """

    def __init__(self, name: str = None):
        self._name = name or "unnamed_router"

        self.callback_query = CallbackQueryHandlersHolder(router=self)
        self.chat_member_updated = ChatMemberUpdatedHandlersHolder(router=self)
        self.chosen_inline_result = ChosenInlineResultHandlersHolder(router=self)
        self.edited_message = EditedMessageHandlersHolder(router=self)
        self.inline_query = InlineQueryHandlersHolder(router=self)
        self.message = MessageHandlersHolder(router=self)
        self.poll = PollHandlersHolder(router=self)

        self._expected_conditions: List[ExpectedCondition] = []

        # This field indicates whether any of router related handlers was
        # called during handling current update. Defaults to `False`. Set to
        # `False` on cleanup (after finishing update processing).
        self._triggered: bool = False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} `{self._name}`"

    @property
    def all_handlers(self) -> List[Handler]:
        return [
            *self.callback_query.handlers,
            *self.chat_member_updated.handlers,
            *self.chosen_inline_result.handlers,
            *self.edited_message.handlers,
            *self.inline_query.handlers,
            *self.message.handlers,
            *self.poll.handlers,
        ]

    def cleanup(self) -> None:
        self._triggered = False

        for handler in self.all_handlers:
            handler._triggered = False

    def add_condition(self, expected_condition: ExpectedCondition):
        self._expected_conditions.append(expected_condition)

    async def feed_update(
        self, client: Client, dispatcher: "dispyro.Dispatcher", update: Update, **deps
    ) -> bool:
        update_type = type(update)
        result = False
        run_logic = dispatcher._run_logic

        for expected_condition in self._expected_conditions:
            if not await expected_condition.check(dispatcher=dispatcher, update=update):
                return result

        if update_type is types.CallbackQuery:
            result = await self.callback_query.feed_update(
                client=client, run_logic=run_logic, update=update, **deps
            )

        elif update_type is types.ChatMemberUpdated:
            result = await self.chat_member_updated.feed_update(
                client=client, run_logic=run_logic, update=update, **deps
            )

        elif update_type is types.ChosenInlineResult:
            result = await self.chosen_inline_result.feed_update(
                client=client, run_logic=run_logic, update=update, **deps
            )

        elif update_type is types.Message:
            update = cast(types.Message, update)

            if update.edit_date:
                result = await self.edited_message.feed_update(
                    client=client, run_logic=run_logic, update=update, **deps
                )

            else:
                result = await self.message.feed_update(
                    client=client, run_logic=run_logic, update=update, **deps
                )

        elif update_type is types.InlineQuery:
            result = await self.inline_query.feed_update(
                client=client, run_logic=run_logic, update=update, **deps
            )

        elif update_type is types.Poll:
            result = await self.poll.feed_update(
                client=client, run_logic=run_logic, update=update, **deps
            )

        return result
