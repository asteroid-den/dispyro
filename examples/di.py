import asyncio
from typing import List

from pyrogram import Client, filters, types

from dispyro import Dispatcher, Router

router = Router()
router.message.filter(filters.me)  # processing only messages from account itself


@router.message(filters.command("numbers", prefixes="."))
async def handler(_, message: types.Message, numbers: List[int]):
    formatted_numbers = ", ".join(map(str, numbers))
    text = f"Entered numbers: {formatted_numbers}"
    await message.edit_text(text=text)


@router.message(filters.command("add", prefixes="."))
async def handler(_, message: types.Message, numbers: List[int]):
    values = message.command[1:]

    if not values:
        await message.delete()
        return

    for value in values:
        if value.isdigit():
            value = int(value)
            numbers.append(value)

    await message.edit_text(text="✅ Numbers added")


@router.message(filters.command("clear", prefixes="."))
async def handler(_, message: types.Message, numbers: List[int]):
    numbers.clear()

    await message.edit_text(text="✅ Numbers list cleared")


async def main():
    client = Client(
        name="dispyro",
        api_id=2040,  # TDesktop api_id, better to be replaced with your value
        api_hash="b18441a1ff607e10a989891a5462e627",  # TDesktop api_hash, better to be replaced with your value
    )
    dispatcher = Dispatcher(client, numbers=[])
    dispatcher.add_router(router)

    await dispatcher.start()


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
