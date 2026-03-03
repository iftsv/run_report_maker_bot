import json
import os
from typing import List, Dict, Optional, Any

USER_LIST_FILE = "user_list.json"
USER_SESSION_FILE = "user_session.json"

def load_json(filename: str, default: Any) -> Any:
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump(default, f)
        return default
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def save_json(filename: str, data: Any):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_tag(user_id: str) -> Optional[str]:
    users = load_json(USER_LIST_FILE, [])
    for user_dict in users:
        if user_id in user_dict:
            return user_dict[user_id]
    return None

def update_user_tag(user_id: str, new_tag: str):
    users = load_json(USER_LIST_FILE, [])
    updated = False
    for user_dict in users:
        if user_id in user_dict:
            user_dict[user_id] = new_tag
            updated = True
            break
    if not updated:
        users.append({user_id: new_tag})
    save_json(USER_LIST_FILE, users)

def get_last_day(user_id: str) -> int:
    sessions = load_json(USER_SESSION_FILE, {})
    return sessions.get(user_id, 0)

def update_last_day(user_id: str, day: int):
    sessions = load_json(USER_SESSION_FILE, {})
    sessions[user_id] = day
    save_json(USER_SESSION_FILE, sessions)
