from typing import Union

import pyrogram
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Poll,
)

import dispyro

from .signatures.handler_callback import (
    CallbackQueryHandlerCallback,
    ChatMemberUpdatedHandlerCallback,
    ChosenInlineResultHandlerCallback,
    EditedMessageHandlerCallback,
    InlineQueryHandlerCallback,
    MessageHandlerCallback,
    PollHandlerCallback,
)

Handler = Union[
    "dispyro.handlers.CallbackQueryHandler",
    "dispyro.handlers.ChatMemberUpdatedHandler",
    "dispyro.handlers.ChosenInlineResultHandler",
    "dispyro.handlers.EditedMessageHandler",
    "dispyro.handlers.InlineQueryHandler",
    "dispyro.handlers.MessageHandler",
    "dispyro.handlers.PollHandler",
]

Callback = Union[
    CallbackQueryHandlerCallback,
    ChatMemberUpdatedHandlerCallback,
    ChosenInlineResultHandlerCallback,
    EditedMessageHandlerCallback,
    InlineQueryHandlerCallback,
    MessageHandlerCallback,
    PollHandlerCallback,
]

Update = Union[
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    Message,
    InlineQuery,
    Poll,
]

AnyFilter = Union[pyrogram.filters.Filter, "dispyro.filters.Filter"]

__all__ = ("Handler", "Callback", "Update", "AnyFilter")
