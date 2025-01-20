import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("Переменная окружения TELEGRAM_TOKEN не установлена!")

if not OPENWEATHER_KEY:
    raise ValueError("Переменная окружения OPENWEATHER_TOKEN не установлена!")
