from typing import Any, List, Protocol

from pyrogram import Client
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Poll,
    User,
)

import dispyro


class CallbackQueryHandlerCallback(Protocol):
    """Signature class for CallbackQueryHandler callback with DI support."""

    async def __call__(self, client: Client, callback_query: CallbackQuery, **deps) -> Any:
        ...


class ChatMemberUpdatedHandlerCallback(Protocol):
    """Signature class for ChatMemberUpdatedHandler callback with DI support."""

    async def __call__(self, client: Client, chat_member_updated: ChatMemberUpdated, **deps) -> Any:
        ...


class ChosenInlineResultHandlerCallback(Protocol):
    """Signature class for ChosenInlineResultHandler callback with DI support."""

    async def __call__(
        self, client: Client, chosen_inline_result: ChosenInlineResult, **deps
    ) -> Any:
        ...


class DeletedMessagesHandlerCallback(Protocol):
    """Signature class for DeletedMessagesHandler callback with DI support."""

    async def __call__(self, client: Client, messages: List[Message], **deps) -> Any:
        ...


class EditedMessageHandlerCallback(Protocol):
    """Signature class for EditedMessageHandler callback with DI support."""

    async def __call__(self, client: Client, message: Message, **deps) -> Any:
        ...


class InlineQueryHandlerCallback(Protocol):
    """Signature class for InlineQueryHandler callback with DI support."""

    async def __call__(self, client: Client, inline_query: InlineQuery, **deps) -> Any:
        ...


class MessageHandlerCallback(Protocol):
    """Signature class for MessageHandler callback with DI support."""

    async def __call__(self, client: Client, message: Message, **deps) -> Any:
        ...


class PollHandlerCallback(Protocol):
    """Signature class for PollHandler callback with DI support."""

    async def __call__(self, client: Client, poll: Poll, **deps) -> Any:
        ...


class RawUpdateHandlerCallback(Protocol):
    """Signature class for RawUpdateHandler callback with DI support."""

    async def __call__(self, client: Client, update: "dispyro.types.PackedRawUpdate", **deps) -> Any:
        ...


class UserStatusHandlerCallback(Protocol):
    """Signature class for UserStatusHandler callback with DI support."""

    async def __call__(self, client: Client, user: User, **deps) -> Any:
        ...
