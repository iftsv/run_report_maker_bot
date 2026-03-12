# Run Report Maker Bot

A streamlined Telegram bot designed to collect daily running reports and format them into structured, beautiful media albums.

## Core Features

- **Workflow-Driven Collection:** Guided FSM (Finite State Machine) flow to ensure all mandatory data is collected (Day number, Tag, Strava screenshot, and Code phrase video).
- **Intelligent Media Ordering:** Automatically organizes media groups with the Strava screenshot first and the code phrase video second, followed by any optional media.
- **Dynamic Captioning:** Generates optimized captions with automated hashtags: `#день{day} #{tag}`.
- **User Authorization:** Restricts bot access to authorized users defined in a local JSON database.
- **Session Persistence:** Remembers each user's progress and suggests the next challenge day automatically.
- **Smart Tags:** Allows users to confirm or update their report hashtags on the fly with interactive suggestions.
- **Input Validation:** Prevents progress if mandatory files (photos/videos) are missing and sanitizes tags for hashtag compatibility.
- **Flexible Media Support:** Easily handles multiple photos and videos in a single Telegram album using `MediaGroupBuilder`.

## Quick Start

1.  **Bot Token:** Get a token from [@BotFather](https://t.me/BotFather).
2.  **Configuration:** Copy `.env.example` to `.env` and fill in your token.
3.  **Run:**
    ```bash
    python main.py
    ```

## Deployment

For production setup instructions (Ubuntu Service, dependencies, etc.), please refer to the [Deployment Guide](deploy_systemd_service.md).