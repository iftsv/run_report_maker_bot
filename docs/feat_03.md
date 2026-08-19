### Intro feat_03.md
This document outlines the plan for **Feature Update 3**: Friendlier Unauthorized-User Messaging for the **Run Report Maker Bot**.

### Phase 6: Global Authorization Middleware
**Mission: Reply to unauthorized users with actionable guidance, on every message, not just `/start`.**

**Problem:** Only `/start` checked `user_list.json` (see [feat_01.md](feat_01.md)), and it replied with a dead-end "Access Denied" message. Every other handler (`/cancel`, and the FSM steps) had no check at all — they were only reachable because `/start` gated entry into the FSM. An unauthorized user sending anything else (a stray message with no active state, or `/cancel`) got no reply at all.

**Objective:** Any message from a `user.id` not present in `user_list.json` gets a clear, single, generic reply telling them to ask the bot admin to add them — regardless of which command or state they hit.

**Implementation:**
1. **Centralized check via middleware** (`main.py`):
   - Added `NOT_AUTHORIZED_MESSAGE`, a generic message with no admin username baked in (keeps it maintenance-free if the admin changes).
   - Registered an `@dp.message.outer_middleware()` handler, `auth_middleware`, right after `bot`/`dp` init. It runs before any handler or FSM state routing:
     - Looks up `json_db.get_user_tag(user_id)` (reused from [feat_01.md](feat_01.md), no new db helper needed).
     - If the user isn't found, replies with `NOT_AUTHORIZED_MESSAGE` and stops propagation (the wrapped handler is never called).
     - If found, calls through to the next handler as normal.
   - This covers every entry point in one place: `/start`, `/cancel`, and any stray text/photo/video sent with no active FSM state.
2. **Removed the now-redundant check** inside `cmd_start` — since the middleware already blocks unauthorized users before the handler runs, `cmd_start` goes back to just clearing state and proceeding straight to the day prompt.

### Key Implementation Details for Developer
* **Why middleware over per-handler checks:** the FSM has multiple entry-adjacent handlers (`/start`, `/cancel`, catch-all state validators). A single outer middleware avoids duplicating the same `get_user_tag` check across all of them and guarantees no new handler can accidentally skip authorization.
* **No changes** to `utils/json_db.py`, `states.py`, or `user_list.json*` — the allowlist format and lookup are unchanged from feat_01.
* **Verification:** temporarily remove your own id from `user_list.json` (or use a fresh test account), run the bot, and confirm `/start`, `/cancel`, and random messages all get `NOT_AUTHORIZED_MESSAGE`. Re-add the id and confirm the full existing flow (`/start` → day → tag → strava photo → video → extra media → generate report) still works unchanged.
