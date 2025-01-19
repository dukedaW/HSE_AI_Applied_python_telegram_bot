from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from src.forms import UserSetUpForm as Form
from src.storage import users_data
from src.storage.user_data import UserData

router = Router(name="User Setup")

@router.message(Command("create_user"))
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
    await message.answer("Спасибо! Информация записана")
    await state.clear()


@router.message(Command("show_profile"))
async def show_profile(message: Message):
    user_id = message.from_user.id
    if user_id not in users_data.keys():
        await message.answer("Данных о Вас нет.\n"
                             "Выполните /create_user")
        return

    user = users_data[user_id]
    await message.answer(f"""
    Ваши данные:
    * Имя: {user.username},
    * Возраст: {user.age},
    * Вес: {user.weight} кг.,
    * Рост: {user.height} см.,
    * Активность: {user.activity_time} мин./день,
    * Город: {user.city}
    """)


@router.message(Command("update_profile"))
async def update_profile(message: Message):

    user_id = message.from_user.id
    if user_id not in users_data.keys():
        await message.answer("Данных о Вас нет.\n"
                             "Выполните /create_user")
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
    await message.reply("Какие данные Вы хотите изменить?", reply_markup=keyboard)


@router.callback_query()
async def handle_update_profile(callback_query: CallbackQuery, state: FSMContext):
    param = callback_query.data

    if param == "cancel":
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

    await state.clear()
    await message.answer("Данные успешно обновлены!")
