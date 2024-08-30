from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict

from pyrogram import Client

import dispyro

from ..enums import MiddlewareState
from .union_types import Update

MiddlewaresContext = Dict["dispyro.middlewares.BaseMiddleware", "MiddlewareContext"]


@dataclass
class MiddlewareContext:
    state: MiddlewareState = MiddlewareState.UNACTIVE
    iterable: AsyncGenerator[Any, Any] | None = None


@dataclass
class UpdateContext:
    client: Client
    update: Update
    data: Dict[str, Any]
    middlewares_context: MiddlewaresContext = field(default_factory=lambda: defaultdict(MiddlewareContext))
