from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from src.forms import LogProgressForm as Form
from src.storage import users_data

router = Router(name="Log progress")


@router.message(Command("log_water"))
async def log_water(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await message.answer("Сколько воды Вы выпили?\n"
                         "Запишите только число.\n")
    await state.set_state(Form.log_water)


@router.message(Form.log_water)
async def update_log_water(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        water = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите только число в мл.")
        return

    users_data[user_id].cur_water += water

    await message.answer(f"Дневная норма воды: {users_data[user_id].water_norm} мл.\n"
                         f"Выпитая вода: {users_data[user_id].cur_water} мл.")
    await state.clear()





