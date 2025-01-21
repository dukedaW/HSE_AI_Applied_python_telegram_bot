from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import aiohttp

from src.forms import LogProgressForm as Form
from src.storage import users_data
from src.handlers.constants import FOOD_URL


router = Router(name="Log progress")


@router.message(Command("log_water"))
async def log_water(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in users_data.keys():
        await message.answer("Данных о Вас нет.\n"
                             "Пожалуйста, выполните /set_profile")
        await state.clear()
        return

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


@router.message(Command("log_calories"))
async def log_calories(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in users_data.keys():
        await message.answer("Данных о Вас нет.\n"
                             "Пожалуйста, выполните /set_profile")
        await state.clear()
        return

    await message.answer("Что Вы выпили/съели?\n"
                         "Запишите только название продукта.\n")

    await state.set_state(Form.log_calories)


@router.message(Form.log_calories)
async def update_log_calories(message: Message, state: FSMContext):
    user_id = message.from_user.id
    food_name = message.text.strip()

    params = {
        "search_terms": food_name,
        "search_simple": 1,
        "action": "process",
        "json": 1
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(FOOD_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                try:
                    product = data["products"][0]
                    product_name = product.get("product_name", "Неизвестный продукт")
                    calories = product["nutriments"].get("energy-kcal_100g", None)
                    if calories is not None:
                        await message.answer(f"{product_name}: {calories} ккал на 100г.")
                    else:
                        await message.answer(f"{product_name} - Неизвестное кол-во ккал")
                        await state.clear()
                        return

                except (IndexError, KeyError):
                    await message.answer("Такой продукт не найден")
                    await state.clear()
                    return

            else:
                await message.answer("Не удалось получить данные о продукте из world.openfoodfacts.org.")
                await state.clear()
                return

    users_data[user_id].cur_calories += calories

    await message.answer(f"Дневная норма калорий: {users_data[user_id].calories_norm} ккал.\n"
                         f"Употребленные калории: {users_data[user_id].cur_calories} ккал.")
    await state.clear()






