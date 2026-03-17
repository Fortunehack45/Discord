# Discord Moderation & Argus Utility Bot

A production-ready Discord bot built with `discord.py` (Python 3.12+) and configured for hosting on Render.

## 🤖 Bot Features & "Commands"

This bot operates primarily through intelligent event handling rather than traditional slash commands (to keep the interface clean and reactive).

### 🛠️ Bot Commands
- `!help` - Show all available bot commands and features.
- `!role` - List all your current server roles.
- `!strike` - Check how many strikes you have left before being kicked.

### 🛡️ Argus Protocol Q&A
The bot is a knowledge expert on the **Argus Protocol**. Mention the bot or type "Argus" along with any of these keywords to get an answer:
- `what is` - General overview of Argus.
- `ghostdag` - Explanation of the GhostDAG consensus.
- `k-parameter` or `optimizer` - How the RL optimization works.
- `agent` - Details on the self-healing state machine.
- `linearizer` - Information on DAG-to-stream data processing.
- `token` - Information about the native AGR token.
- `status` - Current project status and roadmap.
- `website` / `github` - Official links.

### 🚫 Moderation (Automatic)
- **Profanity Filter**: Automatically deletes messages containing blacklisted words.
- **Strike System**: Users get 4 warnings. On the **5th strike**, the bot automatically **kicks** the user (with a DM notification).
- **Dynamic Slowmode**: Automatically adjusts channel slowmode (0s to 120s) based on chat velocity to prevent spam during high activity.

### 🎊 Member Engagement
- **Ultimate Welcome**: Tags new users in the welcome channel, lists server rules, and provides a multi-part introduction to the Argus Protocol.
- **Activity Streak**: Automatically assigns the **"Regular"** role to any member active for 7 consecutive days.
- **Auto-Reply**: Replies with a friendly greeting when the bot is tagged.

## 🛠️ Setup & Deployment

### Local Installation
1. Create a virtual environment: `python -m venv .venv`
2. Activate it: `.venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your `DISCORD_TOKEN`.
5. Run: `python main.py`

### Render Deployment
The bot is configured with `render.yaml` and a built-in Flask "Keep-Alive" server.
1. Connect your GitHub repository to Render.
2. Create a new **Blueprint Instance**.
3. Add your `DISCORD_TOKEN` as an environment variable.

## ⚙️ Required Permissions
Enable these **Privileged Gateway Intents** in the [Discord Developer Portal](https://discord.com/developers/applications):
- **Server Members Intent** (For welcoming and role assignment)
- **Message Content Intent** (For moderation and Q&A)
- **Presence Intent**
