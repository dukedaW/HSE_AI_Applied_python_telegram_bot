from aiogram.fsm.state import State, StatesGroup

class LogProgressForm(StatesGroup):
    log_water = State()
    log_calories = State()
    count_calories = State()
    log_workout_time = State()
