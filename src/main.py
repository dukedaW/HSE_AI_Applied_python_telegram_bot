import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import TELEGRAM_TOKEN
from src.handlers import routers


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
dp.include_routers(*routers)


# dp.message.middleware(LoggingMiddleware())
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
                        "Приветствую!\n"
                        "Добро пожаловать в трекер калорий\n"
                        "/help - ознакомиться со списком команд\n")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/set_profile - создать профиль\n"
        "/show_profile - показать Ваши данные\n"
        "/update_profile - обновить данные в профиле\n"
        "/log_water - обновить данные по выпитой воде, показать статистику\n"
        "/log_calories - обновить данные по употребленным калориям\n"
        "/log_progress - показать прогресс по всем параметрам (вода и калории)"
        # TODO add all commands
    )


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())