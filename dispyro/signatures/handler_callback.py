from typing import Any, Protocol

from pyrogram import Client
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Poll,
)


class CallbackQueryHandlerCallback(Protocol):
    """Signature class for CallbackQuery handler callback with DI support."""

    async def __call__(
        self, client: Client, callback_query: CallbackQuery, **deps
    ) -> Any:
        ...


class ChatMemberUpdatedHandlerCallback(Protocol):
    """Signature class for ChatMemberUpdated handler callback with DI support."""

    async def __call__(
        self, client: Client, chat_member_updated: ChatMemberUpdated, **deps
    ) -> Any:
        ...


class ChosenInlineResultHandlerCallback(Protocol):
    """Signature class for ChosenInlineResult handler callback with DI support."""

    async def __call__(
        self, client: Client, chosen_inline_result: ChosenInlineResult, **deps
    ) -> Any:
        ...


class EditedMessageHandlerCallback(Protocol):
    """Signature class for Message handler (handling edited messages) callback with DI support."""

    async def __call__(self, client: Client, message: Message, **deps) -> Any:
        ...


class InlineQueryHandlerCallback(Protocol):
    """Signature class for InlineQuery handler callback with DI support."""

    async def __call__(
        self, client: Client, inline_query: InlineQuery, **deps
    ) -> Any:
        ...


class MessageHandlerCallback(Protocol):
    """Signature class for Message handler callback with DI support."""

    async def __call__(self, client: Client, message: Message, **deps) -> Any:
        ...


class PollHandlerCallback(Protocol):
    """Signature class for Poll handler callback with DI support."""

    async def __call__(self, client: Client, poll: Poll, **deps) -> Any:
        ...
