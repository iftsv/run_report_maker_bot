### Intro feat_01.md
This document outlines the plan for **Feature Update 1**: User Authorization, Session Tracking, and Smart Dialogues for the **Run Report Maker Bot**.

### Phase 4: User Authorization, Session Persistence & Smart Defaults
**Prompt for Antigravity:**
> **Mission: Implement User Authorization and Persistent Sessions using JSON.**
> 
> **Objective:** Restrict bot access to allowed users, store their custom tags, remember their last reported challenge day, and update the FSM to suggest these values. Allow users to update their tags on the fly.
> 
> **Requirements:**
> 1. **Data Storage Structure:**
>    - Create/Use `user_list.json` to store allowed users and their tags. Format: `[{"123456789": "neofet"}, {"987654321": "runner2"}]` (keys are Telegram User IDs as strings, values are their hashtags without the `#`).
>    - Create/Use `user_session.json` to store the last reported day for each user. Format: `{"123456789": 5, "987654321": 12}`.
>    - Implement utility functions (e.g., in `utils/json_db.py`) to safely read and write to these JSON files.
> 
> 2. **Authorization Check:**
>    - Add a check at the very beginning of the bot's interaction (`/start`).
>    - If the incoming `user.id` is NOT found in `user_list.json`, the bot must reply with an "Access Denied" message and ignore further input.
> 
> 3. **Smart FSM Dialog Updates:**
>    - **Step 1 - Day (Auto-suggest):** Look up the user's last report day in `user_session.json`. 
>       - Calculate `suggested_day = last_day + 1` (default to `1` if no session exists).
>       - Use a `ReplyKeyboardMarkup` with a button (e.g., `Day {suggested_day}`) so they can tap it, OR allow them to type a different number manually.
>    - **Step 2 - Tag/Nickname (Auto-suggest & Update):** 
>       - Look up the user's current tag from `user_list.json`.
>       - Ask the user to confirm their tag. Use a `ReplyKeyboardMarkup` with their current tag as a button (e.g., `neofet`).
>       - If the user taps the button or types the exact same tag, proceed to the next step.
>       - **CRITICAL:** If the user types a *new* tag, the bot must update `user_list.json` with this new value for their `user_id`, and use the new tag for the current report. Remove any `@` or `#` if the user accidentally includes them.
>    - **Step 3 & 4 - Mandatory Media:** Proceed to request Strava screenshot, then Code Phrase video. Remove reply keyboards during these steps using `ReplyKeyboardRemove()`.
> 
> 4. **Updating the Session:**
>    - When the user clicks the "Generate Report" button and the final media group is successfully sent, update the `user_session.json` file with the newly reported day for that `user_id`.

### Key Implementation Details for Developer (Antigravity):
*   **JSON formatting for `user_list`:** Since the format is a list of single-key dictionaries (`[{tlg_user_id: user_tag}]`), write a helper function to iterate through the list to find the user. When updating a tag, modify that specific dictionary in the list and rewrite the file.
*   **Reply Keyboards:** For both the Day and Tag suggestions, use `ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)`. Extract the clean values from the `message.text` in the handlers.
*   **FSM Flow:** The flow should be: `waiting_for_day` -> `waiting_for_tag` -> `waiting_for_strava` -> `waiting_for_video` -> `waiting_for_extra`.