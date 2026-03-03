import os
import asyncio
import logging
from typing import List, Union

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.media_group import MediaGroupBuilder
from dotenv import load_dotenv

from states import ReportStates

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Utils ---

def clean_nickname(nickname: str) -> str:
    """Removes @ prefix from nickname if present."""
    return nickname.lstrip("@").strip()

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Hello! Let's create your run report. \n\nStep 1: Enter the challenge day number (e.g., 5).")
    await state.set_state(ReportStates.waiting_for_day)

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Report creation cancelled. Send /start to begin again.")

@dp.message(StateFilter(ReportStates.waiting_for_day))
async def process_day(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("Please enter a valid number for the day.")
        return
    
    await state.update_data(day=message.text)
    await message.answer("Step 2: Enter your nickname (for the hashtag).")
    await state.set_state(ReportStates.waiting_for_nickname)

@dp.message(StateFilter(ReportStates.waiting_for_nickname))
async def process_nickname(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Please enter your nickname.")
        return
    
    nickname = clean_nickname(message.text)
    await state.update_data(nickname=nickname)
    await message.answer("Step 3: Upload the Strava screenshot.")
    await state.set_state(ReportStates.waiting_for_strava)

@dp.message(StateFilter(ReportStates.waiting_for_strava), F.photo)
async def process_strava(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(strava_photo=photo_id)
    await message.answer("Step 4: Upload the video with the code phrase.")
    await state.set_state(ReportStates.waiting_for_video)

@dp.message(StateFilter(ReportStates.waiting_for_strava))
async def validate_strava(message: types.Message):
    await message.answer("A screenshot (photo) is required. Please upload the Strava screenshot.")

@dp.message(StateFilter(ReportStates.waiting_for_video), F.video)
async def process_video(message: types.Message, state: FSMContext):
    video_id = message.video.file_id
    await state.update_data(phrase_video=video_id)
    await state.update_data(extra_media=[])
    
    # Create keyboard for finishing
    kb = [
        [types.KeyboardButton(text="Generate Report")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    await message.answer(
        "Step 5 (Optional): Upload additional photos or videos. \n"
        "When finished, click the 'Generate Report' button.",
        reply_markup=keyboard
    )
    await state.set_state(ReportStates.waiting_for_extra)

@dp.message(StateFilter(ReportStates.waiting_for_video))
async def validate_video(message: types.Message):
    await message.answer("A video is required. Please upload the video with the code phrase.")

@dp.message(StateFilter(ReportStates.waiting_for_extra), F.text == "Generate Report")
async def process_generate_report(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    day = data.get("day")
    nickname = data.get("nickname")
    strava_photo = data.get("strava_photo")
    phrase_video = data.get("phrase_video")
    extra_media = data.get("extra_media", [])
    
    caption = f"#день{day} #{nickname}"
    
    # Build Media Group
    builder = MediaGroupBuilder(caption=caption)
    
    # 1. Strava Photo
    builder.add_photo(media=strava_photo)
    
    # 2. Phrase Video
    builder.add_video(media=phrase_video)
    
    # 3. Extra Media
    for media_item in extra_media:
        if media_item['type'] == 'photo':
            builder.add_photo(media=media_item['file_id'])
        elif media_item['type'] == 'video':
            builder.add_video(media=media_item['file_id'])
    
    await message.answer_media_group(media=builder.build(), reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    await message.answer("Report generated and sent back to you! Send /start to create another one.")

@dp.message(StateFilter(ReportStates.waiting_for_extra), F.photo | F.video)
async def process_extra_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    extra_media = data.get("extra_media", [])
    
    if message.photo:
        extra_media.append({'type': 'photo', 'file_id': message.photo[-1].file_id})
    elif message.video:
        extra_media.append({'type': 'video', 'file_id': message.video.file_id})
        
    await state.update_data(extra_media=extra_media)
    await message.answer(f"Added. Total extra items: {len(extra_media)}. Send more or click 'Generate Report'.")

@dp.message(StateFilter(ReportStates.waiting_for_extra))
async def validate_extra(message: types.Message):
    await message.answer("Please upload a photo/video or click 'Generate Report'.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
