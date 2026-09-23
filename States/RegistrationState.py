from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_job_title = State()
    waiting_for_cabinet = State()