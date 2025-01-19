from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


from src.bot import bot
from src.forms import UserSetUpForm as Form

router = Router(name="User Setup")

@router.message(Command("create_user"))
async def start_create_user(message: Message, state: FSMContext):
    await bot.send_message(
        chat_id=message.chat.id,
        text="Как вас зовут?",)
    await state.set_state(Form.name)


@router.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await bot.send_message(
        chat_id=message.chat.id,
        text="Сколько Вам лет?",)
    await state.set_state(Form.age)





