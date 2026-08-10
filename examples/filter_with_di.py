import asyncio

from pyrogram import Client, filters, types

from dispyro import Dispatcher, Filter, Router

router = Router()
router.message.filter(filters.me)  # processing only messages from account itself
router.message.filter(filters.command("salad", prefixes=".")) # processing only .salad command

async def fruits_filter_callback(_: Client, message: types.Message, fruits: list[str]):
    # check if all fruits in command are in the list of available fruits
    return message.command is not None and all(fruit in fruits for fruit in message.command[1:])

fruits_filter = Filter(fruits_filter_callback)

@router.message(fruits_filter)
async def handler(_: Client, message: types.Message):
    await message.edit_text(text="😋 Yummy fruit salad")

@router.message(~fruits_filter)
async def handler(_: Client, message: types.Message):
    await message.edit_text(text="😔 We don't have needed fruit")


async def main():
    client = Client(
        name="dispyro",
        api_id=2040,  # TDesktop api_id, better to be replaced with your value
        api_hash="b18441a1ff607e10a989891a5462e627",  # TDesktop api_hash, better to be replaced with your value
    )
    dispatcher = Dispatcher(client, fruits=["apple", "banana", "strawberry"])
    dispatcher.add_router(router)

    await dispatcher.start()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
