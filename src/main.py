import asyncio
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.handlers import routers
from src.bot import bot


dp = Dispatcher()
dp.include_routers(*routers)


# dp.message.middleware(LoggingMiddleware())
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await bot.send_message(
                        chat_id=message.chat.id,
                        text="Приветствую!\n"
                        "Добро пожаловать в трекер калорий\n"
                        "Введите /help для ознакомления со списком команд\n")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="Доступные команды:\n"
        "/start - Начало работы\n"
        "/create_user - создать профиль\n"
    )


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())