from typing import List, Optional

from .filters import Filter
from .middlewares import BaseMiddleware
from .types import AnyFilter


class ProcessingContextHolder:
    def __init__(self, filters: Optional[AnyFilter] = None):
        self.filters = Filter() & filters if filters else Filter()
        self.middlewares: List[BaseMiddleware] = []
        self.outer_middlewares: List[BaseMiddleware] = []

    def filter(self, filter: AnyFilter) -> None:
        self.filters &= filter

    def middleware(self, middleware: BaseMiddleware) -> None:
        self.middlewares.append(middleware)

    def outer_middleware(self, middleware: BaseMiddleware) -> None:
        self.outer_middlewares.append(middleware)
