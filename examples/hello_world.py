import asyncio

from pyrogram import Client, filters, types

from dispyro import Dispatcher, Router

router = Router()
router.message.filter(filters.me)  # processing only messages from account itself


@router.message(filters.command("ping", prefixes="."))
async def handler(_, message: types.Message):
    await message.edit_text(text="🏓 pong!")


async def main():
    client = Client(
        name="dispyro",
        api_id=2040,  # TDesktop api_id, better to be replaced with your value
        api_hash="b18441a1ff607e10a989891a5462e627",  # TDesktop api_hash, better to be replaced with your value
    )
    dispatcher = Dispatcher(client)
    dispatcher.add_router(router)

    await dispatcher.start()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
