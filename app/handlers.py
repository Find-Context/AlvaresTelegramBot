import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.middlewares import TestMiddleware

from utils import bot

router = Router()

router.message.middleware(TestMiddleware())


class Reg(StatesGroup):
    context = State()


# Command handlers
@router.message(CommandStart())
async def send_welcome(message: Message) -> None:
    await message.answer("Hello there! 😊", reply_markup=kb.start)
    message.conf["stop_propagation"] = True


@router.message(Command("find"))
async def send_help(message: Message) -> None:
    await message.answer("Choose type of message:", reply_markup=kb.message_type)


@router.callback_query(F.data == "text")
async def send_text(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Reg.context)
    await callback.message.answer(text="Write your request:", reply_markup=kb.main)


@router.message(Reg.context)
async def register_context(message: Message, state: FSMContext) -> None:
    await state.set_state(Reg.context)
    if message.text.lower() == "cancel":
        await message.answer("Cancelled", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    if message.text == "/find":
        await state.clear()
        await send_help(message)
        return
    if message.text == "/start":
        await state.clear()
        await send_welcome(message)
        return
    await state.update_data(context=message.text)
    data = await state.get_data()

    await state.clear()


@router.message(Command("spin"))
async def spin_luck(message: Message) -> None:
    await message.answer("Лудка епт 🎰")

    attempts = 0
    while True:
        attempts += 1
        dice = await message.answer_dice(emoji="🎰")

        if dice.dice.value == 64:
            await message.answer(f" Jack pot {attempts} attempts")
            break

        await asyncio.sleep(1.5)


import requests
from datetime import datetime

SERVER_URL = "http://100.103.24.101:1000/messages/insert"


@router.message()
async def echo(message: Message) -> None:
    try:
        payload = {
            "chat_id": message.chat.id,
            "message_id": message.message_id,
            "type": "text",
            "text": message.text,
            "created_at": datetime.now().isoformat()
        }

        response = requests.post(SERVER_URL, json=payload)
        # print(f"Message: {message.text}, Type: {type(message.text)}, User: {message.from_user.id}, Chat: {message.chat.id}")
    except TypeError:
        await message.answer("Nice try")
    except Exception as e:
        await message.answer(f"{str(e)}")


@router.callback_query(F.data == "about")
async def send_about(callback: CallbackQuery) -> None:
    await callback.message.answer(
        "It is a bot based on Gema 3 4B model,"
        "you can find context of any type of message in this chat."
        "To use it, write /find and choose type of message."
    )


# In development


@router.message(F.photo)
async def send_photo(message: Message) -> None:
    await message.answer(f"Photo {message.photo[-1].file_id}")
    await message.answer("Image recognition in development!")
