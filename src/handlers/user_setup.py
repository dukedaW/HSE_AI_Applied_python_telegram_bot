from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.forms import UserSetUpForm as Form

router = Router(name="User Setup")

@router.message(Command("create_user"))
async def start_create_user(message: Message, state: FSMContext):
    await message.answer("Как вас зовут?")
    await state.set_state(Form.name)


@router.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько Вам лет?")
    await state.set_state(Form.age)


@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    age = message.text
    await message.reply(f"Привет, {name}! Тебе {age} лет.")
    await state.clear()