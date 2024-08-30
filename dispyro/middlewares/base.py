import contextlib
from typing import Any, AsyncGenerator, Callable, cast

from ..types.contexts import UpdateContext
from ..enums import MiddlewareState

MiddlewareCallable = Callable[[UpdateContext], AsyncGenerator[Any, Any]]


class BaseMiddleware:
    def __init__(self) -> None:
        enter_defined = callable(getattr(self, "enter", None))
        exit_defined = callable(getattr(self, "exit", None))

        if callable(self):
            self.apply: MiddlewareCallable = self.__call__

        else:
            if not enter_defined:

                async def enter(_):
                    pass

                self.enter = enter

            if not exit_defined:

                async def exit(_):
                    pass

                self.exit = exit

            async def apply(context: UpdateContext):
                await self.enter(context)
                yield
                await self.exit(context)

            self.apply = apply

    async def handle(self, context: UpdateContext) -> None:
        middleware_context = context.middlewares_context[self]
        state = middleware_context.state

        if state is MiddlewareState.UNACTIVE:
            iterable = self.apply(context)
            middleware_context.iterable = iterable
            middleware_context.state = MiddlewareState.CALLED_ENTER

            await anext(middleware_context.iterable)

        elif state is MiddlewareState.CALLED_ENTER:
            with contextlib.suppress(StopAsyncIteration):
                iterable = cast(AsyncGenerator[Any, Any], middleware_context.iterable)
                await anext(iterable)

            middleware_context.state = MiddlewareState.CALLED_EXIT
