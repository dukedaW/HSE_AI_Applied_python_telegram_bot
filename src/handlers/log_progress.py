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

    await message.answer("Сколько мл. воды Вы выпили?\n"
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
    user = users_data[user_id]

    water_bar = create_progress_bar(user.cur_water,
                                    user.water_norm)

    await message.answer(f"Прогресс по воде:\n"
                         f"{water_bar} мл.\n")
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

    await state.update_data(calories_per_100_grams=calories)
    await message.answer("Сколько грамм Вы съели?\n"
                         "Введите только число.")
    await state.set_state(Form.count_calories)


@router.message(Form.count_calories)
async def count_calories(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    calories_per_100 = data.get("calories_per_100_grams")
    grams = float(message.text.strip())
    users_data[user_id].cur_calories += calories_per_100 * grams / 100

    user = users_data[user_id]
    calories_bar = create_progress_bar(user.cur_calories,
                                       user.calories_norm)
    await message.answer(f"Прогресс по калориям:\n"
                         f"{calories_bar} ккал.\n")
    await state.clear()


@router.message(Command("check_progress"))
async def log_progress(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in users_data.keys():
        await message.answer("Данных о Вас нет.\n"
                             "Пожалуйста, выполните /set_profile")
        await state.clear()
        return

    user = users_data[user_id]

    calories_bar = create_progress_bar(user.cur_calories,
                                       user.calories_norm)
    water_bar = create_progress_bar(user.cur_water,
                                    user.water_norm)
    await message.answer(f"Прогресс по воде:\n"
                         f"{water_bar} мл.\n\n"
                         f"Прогресс по калориям:\n"
                         f"{calories_bar} ккал.\n")


def create_progress_bar(current: float, total: float, max_length: float = 30.) -> str:
    adaptive_length = min(max_length, total)
    progress = int((current / total) * adaptive_length)
    bar = "█" * progress + "-" * int(adaptive_length - progress)
    cur_total = f"{current:.2f} / {total:.2f}"
    return f"[{bar}] {cur_total}"


@router.message(Command("log_workout"))
async def log_training(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in users_data.keys():
        await message.answer("Данных о Вас нет.\n"
                             "Пожалуйста, выполните /set_profile")
        await state.clear()
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Силовая тренировка", callback_data="power")],
            [InlineKeyboardButton(text="Кардио", callback_data="cardio")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")],
        ]
    )

    await message.answer("Какой был тип тренировки?", reply_markup=keyboard)


@router.callback_query()
async def handle_workout_callback(callback_query: CallbackQuery, state: FSMContext):
    workout_type = callback_query.data

    if workout_type == "cancel":
        await state.clear()
        return

    await callback_query.answer("Сколько минут Вы занимались?")
    await state.update_data(workout_type=workout_type)
    await state.set_state(Form.log_workout_time)


@router.message(Form.log_workout_time)
async def log_workout_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    workout_type = data["workout_type"]
    workout_time = float(message.text.strip())

    users_data[user_id].cur_calories -= 190 * workout_time / 30
    users_data[user_id].cur_water -= 200 * workout_time / 30

    workout_name = {
        "power": " Силовая тренировка",
        "cardio": "Кардио тренировка",
    }[workout_type]

    user = users_data[user_id]

    calories_bar = create_progress_bar(user.cur_calories,
                                       user.calories_norm)
    water_bar = create_progress_bar(user.cur_water,
                                    user.water_norm)

    await message.answer(f"{workout_name}: {workout_time} мин.\n"
                         f"Потрачено приблизительно {190 * workout_time / 30:.2f} ккал.\n"
                         f"Дополнительно следует выпить {200 * workout_time / 30:.2f} мл. воды.\n\n"
                         f"Прогресс по воде:\n"
                         f"{water_bar} мл.\n\n"
                         f"Прогресс по калориям:\n"
                         f"{calories_bar} ккал.\n")
    await state.clear()
