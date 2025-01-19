from aiogram.fsm.state import State, StatesGroup

class UserSetUpForm(StatesGroup):
    age = State()
    weight = State()
    height = State()
    activity_time = State()
    city = State()
    update_param = State()

