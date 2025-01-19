from aiogram.fsm.state import State, StatesGroup

class UserSetUpForm(StatesGroup):
    name = State()
    age = State()
    weight = State()
    height = State()
    activity_time = State()
    city = State()

