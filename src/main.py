import asyncio
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from handlers import routers
from bot import bot


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
        "/form - Пример диалога\n"
        "/keyboard - Пример кнопок\n"
        "/joke - Получить случайную шутку"
    )


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())