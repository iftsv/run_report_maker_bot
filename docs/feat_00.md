### Intro
Initial plan description is in `docs/feat_00.md`

### Bot Name
*   **Run Report Maker Bot**

---

### Phase 1: Dynamic Logic & Flexible Hashtags
**Prompt for Antigravity:**
> **Mission: Develop a Running Report Telegram Bot with dynamic nickname and specific media ordering.**
> 
> **Objective:** Build a bot using `aiogram` that collects running data and returns a structured report to the user.
> 
> **Requirements:**
> 1. **FSM (State Machine) Workflow:**
>    - **Step 1 (Day):** Ask for the challenge day number (e.g., `5`).
>    - **Step 2 (Nickname):** Ask for the user's nickname (to generate `#nickname`).
>    - **Step 3 (Strava - Mandatory):** Request the Strava screenshot.
>    - **Step 4 (Video - Mandatory):** Request the video with the code phrase.
>    - **Step 5 (Extra - Optional):** Allow the user to upload additional photos or videos. Provide a "Generate Report" button to finish.
> 2. **Media Ordering:** When generating the report, the media group **must** be ordered as follows:
>    - 1st: Strava Screenshot (Photo).
>    - 2nd: Code Phrase Video (Video).
>    - 3rd+: Any optional extra photos/videos in the order they were uploaded.
> 3. **Caption Logic:** Attach the final caption to the **first** media item in the group. The caption format: `#день{day} #{nickname}`.
> 4. **Output:** The bot must send this compiled media group back to the user who started the dialog.
> 5. **Config:** Use `.env` for the `BOT_TOKEN`.
> 6. **Python virtual environment:** Use `venv` for the virtual environment.
> 7. **Code complexity:** Use simple and readable code style, without any extra features.

---

### Phase 2: Enhanced Media Handling & User Experience
**Prompt for Antigravity:**
> **Mission: Optimize media collection and validation.**
> 
> **Objective:** Ensure the bot handles multiple optional files correctly and validates mandatory steps.
> 
> **Tasks:**
> 1. Use `MediaGroupBuilder` from `aiogram.utils.media_group` to handle the different media types (photos and videos) in a single album.
> 2. Add validation: If a user sends text during the photo/video steps, the bot should gently remind them that a file is required.
> 3. Add a "Restart" command (`/cancel`) to clear the state if the user makes a mistake.
> 4. Ensure that the nickname input is cleaned (remove "@" if the user includes it) to ensure the hashtag `#nickname` works correctly.

---

### Phase 3: Deployment as an Ubuntu Service
**Prompt for Antigravity:**
> **Mission: Create a production-ready Ubuntu Service for the Running Bot.**
> 
> **Objective:** Automate the setup of the bot as a background service.
> 
> **Tasks:**
> 1. Create virtual environment `venv` and install dependencies.
> 2. Create a `requirements.txt` including `aiogram`, `python-dotenv`, and `pydantic-settings`.
> 3. Generate a `running_bot.service` file.
>    - `User=www-data` (or the appropriate server user).
>    - `WorkingDirectory=/home/user/running_bot`.
>    - `ExecStart=/home/user/running_bot/venv/bin/python3 main.py`.
>    - `Restart=always`.
> 4. Write a `deploy.md` guide explaining:
>    - How to clone the code.
>    - How to create the `.env`.
>    - How to run `systemctl enable` and `systemctl start` to keep the bot running 24/7.

### Key Logic Tip for the Developer (or Antigravity):
To ensure the **Strava screenshot** is always first, use a list to store the `file_id` and `type` for each state. When the "Generate Report" button is clicked, construct the `InputMediaPhoto` and `InputMediaVideo` objects in the exact order: 
1. `strava_photo`
2. `phrase_video`
3. `extend(optional_media_list)`

The caption should be passed to the constructor of the *very first* item in that list so it appears correctly under the whole album in Telegram.