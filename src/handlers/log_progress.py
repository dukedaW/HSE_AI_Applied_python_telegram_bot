from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


router = Router(name="Log progress")


@router.message(Command("log_water"))
async def log_water(message: Message, state: FSMContext):
    user_id = message.from_user.id

