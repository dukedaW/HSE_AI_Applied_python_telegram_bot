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

from src.config import OPENWEATHER_KEY
from src.forms import UserSetUpForm as Form
from src.handlers.constants import WEATHER_URL
from src.storage import users_data
from src.storage.user_data import UserData


router = Router(name="User Setup")

@router.message(Command("set_profile"))
async def create_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username

    users_data[user_id] = UserData(
        username=username,
    )

    await message.answer(f"Добрый день, {username}\n"
                        "введите некоторые данные о себе")
    await message.answer("Сколько Вам лет?")
    await state.set_state(Form.age)


@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        age = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите только число")
        return

    users_data[user_id].age = age
    await message.answer("Какой у Вас вес (в кг.)?")
    await state.set_state(Form.weight)


@router.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        weight = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите только число")
        return

    users_data[user_id].weight = weight
    await message.answer("Какой у Вас рост (в см.)?")
    await state.set_state(Form.height)


@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        height = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите только число")
        return

    users_data[user_id].height = height
    await message.answer("Сколько минут в день Вы активны (спорт, ходьба и.т.д.)?")
    await state.set_state(Form.activity_time)


@router.message(Form.activity_time)
async def process_activity_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        activity_time = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите только число")
        return

    users_data[user_id].activity_time = activity_time
    await message.answer("В каком городе Вы живете?")
    await state.set_state(Form.city)


@router.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    user_id = message.from_user.id
    users_data[user_id].city = message.text
    await set_daily_norms(user_id)
    await message.answer("Спасибо! Информация записана.")
    await state.clear()


async def set_daily_norms(user_id: int):

    weight = users_data[user_id].weight
    activity_time = users_data[user_id].activity_time
    city = users_data[user_id].city
    age = users_data[user_id].age
    height = users_data[user_id].height

    url = WEATHER_URL.format(city=city,
                             api_key=OPENWEATHER_KEY)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                weather_data = await response.json()
            else:
                raise ValueError("Couldn't get weather data")

    temperature = weather_data['main']['temp']

    users_data[user_id].water_norm = \
        weight * 30 + \
        activity_time // 30 * 500 + \
        500 * (temperature > 25.0)

    users_data[user_id].calories_norm = \
        10 * weight + 6.25 * height - 5 * age


@router.message(Command("show_profile"))
async def show_profile(message: Message):
    user_id = message.from_user.id
    if user_id not in users_data.keys():
        await message.answer("Данных о Вас нет.\n"
                             "Выполните /set_profile")
        return

    user = users_data[user_id]
    await message.answer(f"""
    Ваши данные:
    * Имя: {user.username}
    * Возраст: {user.age}
    * Вес: {user.weight} кг.
    * Рост: {user.height} см.
    * Активность: {user.activity_time} мин./день
    * Город: {user.city}
    * Рассчитанная дневная норма калорий: {user.calories_norm} ккал.
    * Рассчитанная дневная норма воды: {user.water_norm} мл.
    """)


@router.message(Command("update_profile"))
async def update_profile(message: Message):

    user_id = message.from_user.id
    if user_id not in users_data.keys():
        await message.answer("Данных о Вас нет.\n"
                             "Выполните /set_profile")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Возраст", callback_data="age")],
            [InlineKeyboardButton(text="Вес", callback_data="weight")],
            [InlineKeyboardButton(text="Рост", callback_data="height")],
            [InlineKeyboardButton(text="Дневную активность", callback_data="activity_time")],
            [InlineKeyboardButton(text="Город", callback_data="city")],
            [InlineKeyboardButton(text="Отменить", callback_data="cancel")],
        ]
    )
    await message.answer("Какие данные Вы хотите изменить?", reply_markup=keyboard)


@router.callback_query()
async def handle_update_profile(callback_query: CallbackQuery, state: FSMContext):
    param = callback_query.data

    if param == "cancel":
        await state.clear()
        return

    param_name = {
        "age": "новый Возраст",
        "weight": "новый Вес",
        "height": "новый Рост",
        "activity_time": "новую Дневную активность",
        "city": "новый Город",
    }[param]

    await callback_query.answer(f"Пожалуйста, введите {param_name}")
    await state.update_data(param=param)
    await state.set_state(Form.update_param)


@router.message(Form.update_param)
async def set_new_param(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    param = data.get("param")

    try:
        param_type = type(users_data[user_id][param])
        users_data[user_id][param] = param_type(message.text)
    except ValueError:
        raise ValueError('Trying to set param of wrong type')

    await set_daily_norms(user_id)
    await message.answer("Информация успешно обновлена!")
    await state.clear()
