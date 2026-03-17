# Discord Moderation & Utility Bot

A Python Discord bot built with `discord.py`.

## Features
- **Profanity Filter**: Deletes messages containing blacklisted words.
- **Strike System**: 5 strikes results in an automatic kick.
- **Welcome System**: Personalized DM and channel welcome messages.
- **Mention Response**: Interaction when tagged.
- **Dynamic Slowmode**: Adjusts message frequency limits based on chat intensity.

## Installation
1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` with your `DISCORD_TOKEN`.
3. Run the bot: `python main.py`

## Intents Required
Ensure the following intents are enabled in the Discord Developer Portal:
- `Server Members Intent`
- `Message Content Intent`
