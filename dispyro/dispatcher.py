from typing import Any, Dict, List

from pyrogram import Client, handlers, idle
from pyrogram.handlers.handler import Handler

from .enums import RunLogic
from .router import Router
from .union_types import Update


class Dispatcher:
    """Main class to interract with API. Dispatcher itself cannot be used to
    register handlers, so routers must be attached to it.
    """

    def __init__(
        self,
        *clients: Client,
        ignore_preparation: bool = False,
        clear_on_prepare: bool = True,
        run_logic: RunLogic = RunLogic.ONE_RUN_PER_EVENT,
        **deps
    ):
        self.routers: List[Router] = []
        self._clients: List[Client] = []
        self._deps: Dict[str, Any] = deps

        self._ignore_preparation = ignore_preparation
        self._clear_on_prepare = clear_on_prepare
        self._run_logic = run_logic

        if ignore_preparation:
            self._clients = list(clients)

        else:
            for client in clients:
                client = self.prepare_client(
                    client=client, clear_handlers=clear_on_prepare
                )
                self._clients.append(client)

    def prepare_client(self, client: Client, clear_handlers: bool = True) -> Client:
        async def handler(client: Client, update: Update):
            await self.feed_update(client=client, update=update)

        handler_types: List[Handler] = [
            handlers.CallbackQueryHandler,
            handlers.ChatMemberUpdatedHandler,
            handlers.ChosenInlineResultHandler,
            handlers.EditedMessageHandler,
            handlers.InlineQueryHandler,
            handlers.MessageHandler,
            handlers.PollHandler,
        ]

        group = 0

        if clear_handlers:
            client.dispatcher.groups.clear()

        else:
            groups = list(client.dispatcher.groups.keys())

            if groups:
                group = max(groups) + 1

        for handler_type in handler_types:
            client.add_handler(handler_type(handler), group=group)

        return client

    def add_router(self, router: Router):
        self.routers.append(router)

    def add_routers(self, *routers: Router):
        self.routers.extend(routers)

    def cleanup(self) -> None:
        for router in self.routers:
            router.cleanup()

    async def feed_update(self, client: Client, update: Update) -> None:
        for router in self.routers:
            result = await router.feed_update(
                client=client, dispatcher=self, update=update, **self._deps
            )

            if self._run_logic is RunLogic.ONE_RUN_PER_EVENT and result:
                break

        self.cleanup()

    async def start(
        self,
        *clients: Client,
        ignore_preparation: bool = None,
        only_start: bool = False
    ) -> None:
        self.cleanup()

        if ignore_preparation is None:
            ignore_preparation = self._ignore_preparation

        if ignore_preparation:
            clients = list(clients)

        else:
            clients = [
                self.prepare_client(
                    client=client, clear_handlers=self._clear_on_prepare
                )
                for client in clients
            ]

        clients = self._clients + clients

        for client in clients:
            if not client.is_connected:
                await client.start()

        if not only_start:
            await idle()
