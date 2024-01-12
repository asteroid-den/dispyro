import asyncio
from typing import Any, Callable, Coroutine, Dict, List, Union

from pyrogram import Client, handlers, idle
from pyrogram.handlers.handler import Handler
from pyrogram.raw import base

from .enums import RunLogic
from .handlers_holders import (
    CallbackQueryHandlersHolder,
    ChatMemberUpdatedHandlersHolder,
    ChosenInlineResultHandlersHolder,
    DeletedMessagesHandlersHolder,
    EditedMessageHandlersHolder,
    InlineQueryHandlersHolder,
    MessageHandlersHolder,
    PollHandlersHolder,
    RawUpdateHandlersHolder,
    UserStatusHandlersHolder,
)
from .router import Router
from .types import PackedRawUpdate, Update


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
        self._default_router = Router(name="root_router")
        self.routers: List[Router] = [self._default_router]
        self._clients: List[Client] = []
        self._deps: Dict[str, Any] = deps

        self._ignore_preparation = ignore_preparation
        self._clear_on_prepare = clear_on_prepare
        self._run_logic = run_logic

        if ignore_preparation:
            self._clients = list(clients)

        else:
            for client in clients:
                client = self.prepare_client(client=client, clear_handlers=clear_on_prepare)
                self._clients.append(client)

    @property
    def callback_query(self) -> CallbackQueryHandlersHolder:
        return self._default_router.callback_query

    @property
    def chat_member_updated(self) -> ChatMemberUpdatedHandlersHolder:
        return self._default_router.chat_member_updated

    @property
    def chosen_inline_result(self) -> ChosenInlineResultHandlersHolder:
        return self._default_router.chosen_inline_result

    @property
    def deleted_messages(self) -> DeletedMessagesHandlersHolder:
        return self._default_router.deleted_messages

    @property
    def edited_message(self) -> EditedMessageHandlersHolder:
        return self._default_router.edited_message

    @property
    def inline_query(self) -> InlineQueryHandlersHolder:
        return self._default_router.inline_query

    @property
    def message(self) -> MessageHandlersHolder:
        return self._default_router.message

    @property
    def poll(self) -> PollHandlersHolder:
        return self._default_router.poll

    @property
    def raw_update(self) -> RawUpdateHandlersHolder:
        return self._default_router.raw_update

    @property
    def user_status(self) -> UserStatusHandlersHolder:
        return self._default_router.user_status

    def _make_handler(self, handler_type: Handler) -> Callable[[Client, Update], Coroutine]:
        if handler_type is handlers.RawUpdateHandler:

            async def handler(
                client: Client,
                update: base.Update,
                users: Dict[int, base.User],
                chats: Dict[int, base.Chat],
            ):
                packed_update = PackedRawUpdate(update=update, users=users, chats=chats)
                await self.feed_update(
                    client=client, update=packed_update, handler_type=handler_type
                )

        else:

            async def handler(client: Client, update: Update):
                await self.feed_update(client=client, update=update, handler_type=handler_type)

        return handler

    def prepare_client(self, client: Client, clear_handlers: bool = True) -> Client:
        handler_types: List[Handler] = [
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

    async def feed_update(self, client: Client, update: Update, handler_type: Handler) -> None:
        for router in self.routers:
            result = await router.feed_update(
                client=client,
                dispatcher=self,
                update=update,
                handler_type=handler_type,
                **self._deps,
            )

            if self._run_logic is RunLogic.ONE_RUN_PER_EVENT and result:
                break

        self.cleanup()

    async def start(
        self,
        *clients: Client,
        ignore_preparation: bool = None,
        only_start: bool = False,
    ) -> None:
        self.cleanup()

        if ignore_preparation is None:
            ignore_preparation = self._ignore_preparation

        if ignore_preparation:
            clients = list(clients)

        else:
            clients = [
                self.prepare_client(client=client, clear_handlers=self._clear_on_prepare)
                for client in clients
            ]

        clients = self._clients + clients

        for client in clients:
            if not client.is_connected:
                await client.start()

        if not only_start:
            await idle()
