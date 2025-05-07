from dataclasses import dataclass
from typing import Dict, Generic, TypeVar

from pyrogram.raw.base import Chat, User
from pyrogram.raw.core import TLObject

T = TypeVar("T", bound=TLObject)


@dataclass
class PackedRawUpdate(Generic[T]):
    update: T
    users: Dict[int, User]
    chats: Dict[int, Chat]
