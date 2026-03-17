# Discord Moderation & Utility Bot

A Python Discord bot built with `discord.py` (Python 3.12+).

## Features
- **Profanity Filter**: Deletes messages containing blacklisted words.
- **Strike System**: 5 strikes results in an automatic kick.
- **Welcome System**: Personalized DM and channel welcome messages.
- **Mention Response**: Bot replies when tagged.
- **Dynamic Slowmode**: Adjusts message rate limits based on chat activity.

## Setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your `DISCORD_TOKEN`.
5. Run the bot: `python main.py`

## Required Discord Intents
Enable these in the [Discord Developer Portal](https://discord.com/developers/applications):
- **Server Members Intent**
- **Message Content Intent**
