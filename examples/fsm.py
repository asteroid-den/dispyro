import asyncio

from pyrogram import Client, filters, types
from dispyro import Dispatcher, Router
from dispyro.fsm import FSMContext
from dispyro.fsm.state import State, StatesGroup

router = Router()
router.message.filter(filters.private)  # processing only messages from private chats


class Form(StatesGroup):
    name = State()
    age = State()


@router.message(filters.command("start"))
async def command_start(_: Client, message: types.Message, state: FSMContext):
    await state.set(Form.name)
    await message.reply(text="Hello! What's your name?")


@router.message(filters.command("stop"))
async def command_stop(_: Client, message: types.Message, state: FSMContext):
    current_state = await state.get()

    if current_state is None:
        return

    await state.clear()

    await message.reply("Fine... See you later 😔")


@router.message(Form.name)
async def process_name(_: Client, message: types.Message, state: FSMContext):
    await state.update_data({"name": message.content})
    await state.set(Form.age)

    await message.reply(
        f"Nice to meet you, {message.content}!\nHow old are you?",
    )


@router.message(Form.age)
async def process_age(_: Client, message: types.Message, state: FSMContext):
    data = await state.get_data()

    await state.clear()

    await message.reply(
        f"Now I know your name is {data['name']} and you are {message.content} years old!",
    )


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
