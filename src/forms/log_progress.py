from aiogram.fsm.state import State, StatesGroup

class LogProgressForm(StatesGroup):
    log_water = State()
    log_calories = State()
