# This file defines core of filtering utility named `expected conditions`
# (abbreviated EC). This utility provides you ability to specify custom
# dispatch logic based on dispatching system state. You can find more detailed
# info in classes and functions docstrings.

from typing import Optional, Union

from . import utils
from .dispatcher import Dispatcher
from .router import Router
from .signatures import FilterCallback
from .union_types import Update
from .enums import ExpectedConditionCheckType


# too long notation when mentioning enum itself
ITER_ALL_ROUTERS = ExpectedConditionCheckType.ITER_ALL_ROUTERS
PUT_ACTUAL_ROUTER = ExpectedConditionCheckType.PUT_ACTUAL_ROUTER

RouterLike = Union[Router, str]


class ExpectedCondition:
    """Defines specific condition checked before router triggering."""

    def __init__(
        self,
        condition_callback: FilterCallback,
        check_type: ExpectedConditionCheckType,
        router: Router = None,
    ):
        if check_type is PUT_ACTUAL_ROUTER and router is None:
            raise ValueError("you must provide actual router for this check type")

        self._callback: FilterCallback = utils.safe_call(callable=condition_callback)
        self._check_type = check_type
        self._router = router

    def __invert__(self) -> "InvertedExpectedCondition":
        return InvertedExpectedCondition(
            condition_callback=self._callback,
            check_type=self._check_type,
            router=self._router,
        )

    async def check(self, dispatcher: Dispatcher, update: Update) -> bool:
        client = dispatcher.client
        deps = dispatcher._deps
        if self._check_type is ITER_ALL_ROUTERS:
            for router in dispatcher.routers:
                result = await self._callback(client, update, router, **deps)

                if result:
                    return result

            return False

        elif self._check_type is PUT_ACTUAL_ROUTER:
            return await self._callback(client, update, self._router, **deps)


class InvertedExpectedCondition(ExpectedCondition):
    def __invert__(self) -> ExpectedCondition:
        return ExpectedCondition(
            condition_callback=self._callback,
            check_type=self._check_type,
            router=self._router,
        )

    async def check(self, dispatcher: Dispatcher, update: Update) -> bool:
        client = dispatcher.client
        deps = dispatcher._deps
        if self._check_type == ITER_ALL_ROUTERS:
            for router in dispatcher.routers:
                result = not await self._callback(client, update, router)

                if result:
                    return result

            return True

        elif self._check_type == PUT_ACTUAL_ROUTER:
            return not await self._callback(client, update, self._router, **deps)


def router_is_triggered(related_router: RouterLike) -> ExpectedCondition:
    """Makes `ExpectedCondition` object which throws `True` if specified router
    was triggered during processing current update.

    IMPORTANT: if specified router goes after router that examines this condition,
    it won't work. Trigger check can only be performed backwards according to
    checks sequence.
    """
    router_id: Optional[int] = None
    router_name: Optional[str] = None

    if type(related_router) is Router:
        router_id = id(related_router)

    elif type(related_router) is str:
        router_name = related_router

        if router_name == "unnamed_router":
            raise ValueError("only named routers can be mentioned")

    else:
        raise ValueError(
            f"`related_router` type can be only `str` or `Router`, got `{type(related_router)}`"
        )

    async def callback(_, __, router: Router) -> bool:
        nonlocal router_id, router_name

        if router_id:
            return id(router) == router_id and router._triggered

        elif router_name:
            return router._name == router_name and router._triggered

    return ExpectedCondition(
        condition_callback=callback, check_type=ITER_ALL_ROUTERS, router=related_router
    )


def router_is_not_triggered(related_router: RouterLike) -> InvertedExpectedCondition:
    return ~router_is_triggered(related_router=related_router)
