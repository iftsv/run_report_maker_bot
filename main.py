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
from utils import json_db

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Utils ---

def clean_tag(tag: str) -> str:
    """Removes @ and # prefix from tag if present."""
    return tag.lstrip("@#").strip()

# --- Handlers ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    user_id = str(message.from_user.id)
    current_tag = json_db.get_user_tag(user_id)
    
    if current_tag is None:
        await message.answer("Access Denied. You are not on the authorized user list.")
        return

    last_day = json_db.get_last_day(user_id)
    suggested_day = last_day + 1
    
    kb = [[types.KeyboardButton(text=f"Day {suggested_day}")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        f"Hello! Let's create your run report. \n\n"
        f"Step 1: Enter the challenge day number (suggested: {suggested_day}).",
        reply_markup=keyboard
    )
    await state.set_state(ReportStates.waiting_for_day)

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Report creation cancelled. Send /start to begin again.", reply_markup=types.ReplyKeyboardRemove())

@dp.message(StateFilter(ReportStates.waiting_for_day))
async def process_day(message: types.Message, state: FSMContext):
    text = message.text
    if text.startswith("Day "):
        day_str = text.split(" ")[1]
    else:
        day_str = text
        
    if not day_str.isdigit():
        await message.answer("Please enter a valid number for the day.")
        return
    
    await state.update_data(day=day_str)
    
    user_id = str(message.from_user.id)
    current_tag = json_db.get_user_tag(user_id)
    
    kb = [[types.KeyboardButton(text=current_tag)]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    await message.answer(
        f"Step 2: Confirm or update your tag (current: #{current_tag}).",
        reply_markup=keyboard
    )
    await state.set_state(ReportStates.waiting_for_tag)

@dp.message(StateFilter(ReportStates.waiting_for_tag))
async def process_tag(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Please enter or confirm your tag.")
        return
    
    new_tag = clean_tag(message.text)
    user_id = str(message.from_user.id)
    old_tag = json_db.get_user_tag(user_id)
    
    if new_tag != old_tag:
        json_db.update_user_tag(user_id, new_tag)
        await message.answer(f"Tag updated to #{new_tag}.")
    
    await state.update_data(tag=new_tag)
    await message.answer("Step 3: Upload the Strava screenshot.", reply_markup=types.ReplyKeyboardRemove())
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
    tag = data.get("tag")
    strava_photo = data.get("strava_photo")
    phrase_video = data.get("phrase_video")
    extra_media = data.get("extra_media", [])
    
    caption = f"#день{day} #{tag}"
    
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
    
    media_group = builder.build()
    await message.answer_media_group(media=media_group, reply_markup=types.ReplyKeyboardRemove())
    
    # Update session - last reported day
    user_id = str(message.from_user.id)
    json_db.update_last_day(user_id, int(day))
    
    await state.clear()
    await message.answer("Report generated and sent back to you! Your session has been updated. Send /start for next time.")

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
