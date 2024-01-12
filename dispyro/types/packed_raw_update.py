from dataclasses import dataclass
from typing import Dict, Generic, TypeVar

from pyrogram.raw.base import Chat, Update, User

T = TypeVar("T", bound=Update)


@dataclass
class PackedRawUpdate(Generic[T]):
    update: T
    users: Dict[int, User]
    chats: Dict[int, Chat]
