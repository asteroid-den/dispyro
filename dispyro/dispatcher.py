from functools import cached_property
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, Union

from pyrogram import Client, handlers, idle
from pyrogram.handlers.handler import Handler as PyrogramHandler
from pyrogram.raw import base, core

from .enums import RunLogic
from .processing_context_holder import ProcessingContextHolder
from .router import Router
from .types import PackedRawUpdate, Update
from .types.contexts import UpdateContext

PyrogramHandlerCallback = Callable[[Client, Update], Awaitable[Any]]
PyrogramRawHandlerCallback = Callable[[Client, core.TLObject, Dict[int, base.User], Dict[int, base.Chat]], Awaitable]
AnyPyrogramHandlerCallback = Union[PyrogramHandlerCallback, PyrogramRawHandlerCallback]


class Dispatcher:
    """Main class to interract with API. Can register handlers by itself and
    attach other routers.
    """

    def __init__(
        self,
        *clients: Client,
        ignore_preparation: bool = False,
        clear_on_prepare: bool = True,
        run_logic: RunLogic = RunLogic.ONE_RUN_PER_EVENT,
        **deps,
    ):
        self.routers: List[Router] = []
        self._clients: List[Client] = []
        self._deps: Dict[str, Any] = deps

        self.callback_query = ProcessingContextHolder()
        self.chat_member_updated = ProcessingContextHolder()
        self.chosen_inline_result = ProcessingContextHolder()
        self.deleted_messages = ProcessingContextHolder()
        self.edited_message = ProcessingContextHolder()
        self.inline_query = ProcessingContextHolder()
        self.message = ProcessingContextHolder()
        self.poll = ProcessingContextHolder()
        self.raw_update = ProcessingContextHolder()
        self.user_status = ProcessingContextHolder()

        self._ignore_preparation = ignore_preparation
        self._clear_on_prepare = clear_on_prepare
        self._run_logic = run_logic

        if ignore_preparation:
            self._clients = list(clients)

        else:
            for client in clients:
                client = self.prepare_client(client=client, clear_handlers=clear_on_prepare)
                self._clients.append(client)

    @cached_property
    def processing_context_correlation(self) -> Dict[Type[PyrogramHandler], ProcessingContextHolder]:
        return {
            handlers.CallbackQueryHandler: self.callback_query,
            handlers.ChatMemberUpdatedHandler: self.chat_member_updated,
            handlers.ChosenInlineResultHandler: self.chosen_inline_result,
            handlers.DeletedMessagesHandler: self.deleted_messages,
            handlers.EditedMessageHandler: self.edited_message,
            handlers.InlineQueryHandler: self.inline_query,
            handlers.MessageHandler: self.message,
            handlers.PollHandler: self.poll,
            handlers.RawUpdateHandler: self.raw_update,
            handlers.UserStatusHandler: self.user_status,
        }

    def _make_handler(self, handler_type: Type[PyrogramHandler]) -> AnyPyrogramHandlerCallback:
        if handler_type is handlers.RawUpdateHandler:

            async def handler(
                client: Client,
                update: core.TLObject,
                users: Dict[int, base.User],
                chats: Dict[int, base.Chat],
            ):
                packed_update = PackedRawUpdate(update=update, users=users, chats=chats)
                await self.feed_update(client=client, update=packed_update, handler_type=handler_type)

        else:

            async def handler(client: Client, update: Update):
                await self.feed_update(client=client, update=update, handler_type=handler_type)

        return handler

    def prepare_client(self, client: Client, clear_handlers: bool = True) -> Client:
        handler_types: List[Type[PyrogramHandler]] = [
            handlers.CallbackQueryHandler,
            handlers.ChatMemberUpdatedHandler,
            handlers.ChosenInlineResultHandler,
            handlers.DeletedMessagesHandler,
            handlers.EditedMessageHandler,
            handlers.InlineQueryHandler,
            handlers.MessageHandler,
            handlers.PollHandler,
            handlers.RawUpdateHandler,
            handlers.UserStatusHandler,
        ]

        group = 0

        if clear_handlers:
            client.dispatcher.groups.clear()

        else:
            groups = list(client.dispatcher.groups.keys())

            if groups:
                group = max(groups) + 1

        for handler_type in handler_types:
            handler = self._make_handler(handler_type=handler_type)

            client.add_handler(handler_type(handler), group=group)

        return client

    def add_router(self, router: Router):
        self.routers.append(router)

    def add_routers(self, *routers: Router):
        self.routers.extend(routers)

    def cleanup(self) -> None:
        for router in self.routers:
            router.cleanup()

    async def feed_update(self, client: Client, update: Update, handler_type: Type[PyrogramHandler]) -> None:
        processing_context = self.processing_context_correlation[handler_type]
        context = UpdateContext(client=client, update=update, data=self._deps)

        for middleware in processing_context.outer_middlewares:
            await middleware.handle(context=context)

        filters_passed = await processing_context.filters(client, update, **self._deps)

        if not filters_passed:
            return

        for middleware in processing_context.middlewares:
            await middleware.handle(context=context)

        for router in self.routers:
            result = await router.feed_update(context=context, dispatcher=self, handler_type=handler_type)

            if self._run_logic is RunLogic.ONE_RUN_PER_EVENT and result:
                break

        self.cleanup()

    async def start(
        self,
        *clients: Client,
        ignore_preparation: Optional[bool] = None,
        only_start: bool = False,
    ) -> None:
        self.cleanup()

        if ignore_preparation is None:
            ignore_preparation = self._ignore_preparation

        if ignore_preparation:
            clients_list = list(clients)

        else:
            clients_list = [
                self.prepare_client(client=client, clear_handlers=self._clear_on_prepare) for client in clients
            ]

        clients_list = self._clients + clients_list

        for client in clients:
            if not client.is_connected:
                await client.start()

        if not only_start:
            await idle()
