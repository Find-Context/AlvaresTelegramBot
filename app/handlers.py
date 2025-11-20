# import ollama

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.middlewares import TestMiddleware

from utils.db_service import db

from utils.bot_service import bs

router = Router()
# state_router = Router()

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

    message_id = db.get_best_fit(data["context"], message.chat.id)

    # find message with this id and send it to user

    await bs.bot.send_message(
        chat_id=message.chat.id, text="Abra kadabra", reply_to_message_id=message_id
    )

    # for msg in messages:
    #     message_list += msg.text + "\n"
    # prompt = f"""
    # Ты — интеллектуальный помощник. Найди наиболее релевантное сообщение по смыслу из списка, которое лучше всего соответствует запросу пользователя.
    #
    # Запрос пользователя:
    # "{data["context"]}"
    #
    # Сообщения в чате:
    # {message_list}
    #
    # Ответь только текст наиболее подходящего сообщения.
    # """
    #
    # try:
    #     assistant_response = ollama.generate(
    #         model="gemma3:latest",
    #         prompt=prompt,
    #         stream=False,
    #         options={
    #             "temperature": 0.2,
    #             "num_predict": 2000
    #         }
    #     )
    #
    #     await message.answer(assistant_response["response"])
    #
    # except TypeError:
    #     await message.answer("Nice try")
    # except ollama.ResponseError as e:
    #     await message.answer(f"{e.error}")
    # except Exception as e:
    #     await message.answer(f"{str(e)}")

    await state.clear()


@router.message()
async def echo(message: Message) -> None:
    try:
        db.save_message(
            message_id=message.message_id, text=message.text, chat_id=message.chat.id
        )
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
