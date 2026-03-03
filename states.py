from aiogram.fsm.state import State, StatesGroup

class ReportStates(StatesGroup):
    waiting_for_day = State()
    waiting_for_tag = State()
    waiting_for_strava = State()
    waiting_for_video = State()
    waiting_for_extra = State()
