import discord
from discord.ext import commands
import os
import json
from typing import Dict, List
from datetime import datetime, timedelta, timezone, date
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WELCOME_CHANNEL_NAME = os.getenv('WELCOME_CHANNEL_NAME', 'general-discussion')

# Role name for members who are active 7 consecutive days
ACTIVITY_ROLE_NAME = "Regular"
STREAK_DAYS_REQUIRED = 7

# ---------------------------------------------------------------------------
# Bot setup
# ---------------------------------------------------------------------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# ---------------------------------------------------------------------------
# Profanity list
# ---------------------------------------------------------------------------
BANNED_WORDS = [
    # General profanity
    'shit', 'bullshit', 'shithead', 'shitface',
    'fuck', 'fucker', 'fucking', 'motherfucker', 'fuckface', 'fuckhead',
    'ass', 'asshole', 'asshat', 'asswipe',
    'bitch', 'bitches', 'son of a bitch',
    'bastard', 'dick', 'dickhead', 'cock', 'cunt', 'pussy', 'prick',
    'damn', 'goddamn', 'hell',
    'crap', 'piss', 'pissed',
    # Slurs & hate speech
    'nigga', 'nigger', 'nigg',
    'faggot', 'fag', 'dyke',
    'retard', 'retarded',
    'spic', 'chink', 'kike', 'gook', 'wetback', 'cracker', 'honky',
    'whore', 'slut', 'hoe', 'skank', 'thot',
    # Sexual
    'sex', 'sexy', 'penis', 'vagina', 'boobs', 'tits', 'porn', 'nude', 'nudes',
    # Violence / threats
    'kill yourself', 'kys', 'go die', 'kill urself',
]


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------
STRIKES_FILE = 'strikes.json'
ACTIVITY_FILE = 'activity.json'


def _load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def _save_json(path: str, data: dict):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def load_strikes() -> Dict[str, int]:
    return _load_json(STRIKES_FILE)


def save_strikes(strikes: Dict[str, int]):
    _save_json(STRIKES_FILE, strikes)


def load_activity() -> Dict[str, List[str]]:
    """Returns {user_id: [date_str, ...]} sorted oldest→newest."""
    return _load_json(ACTIVITY_FILE)


def save_activity(activity: Dict[str, List[str]]):
    _save_json(ACTIVITY_FILE, activity)


# ---------------------------------------------------------------------------
# Activity / streak logic
# ---------------------------------------------------------------------------
def record_activity(user_id: str) -> int:
    """
    Record that *user_id* was active today.
    Returns the current consecutive-day streak.
    """
    activity = load_activity()
    today_str = date.today().isoformat()          # e.g. "2025-03-17"

    dates: List[str] = activity.get(user_id, [])

    # Avoid duplicate entries for the same day
    if today_str not in dates:
        dates.append(today_str)
        # Keep only the last 30 days to avoid unbounded growth
        all_sorted: List[str] = sorted(dates)
        dates = all_sorted[-30:] # type: ignore
        activity[user_id] = dates
        save_activity(activity)
    else:
        dates = sorted(dates)

    return _count_streak(dates)


def _count_streak(sorted_dates: List[str]) -> int:
    """Count consecutive days ending today (or yesterday at most)."""
    if not sorted_dates:
        return 0

    today = date.today()
    streak = 0
    expected = today

    for date_str in reversed(sorted_dates):
        d = date.fromisoformat(date_str)
        if d == expected:
            streak = streak + 1 # type: ignore
            expected = expected - timedelta(days=1) # type: ignore
        elif d < expected:
            break   # gap — streak broken

    return streak


async def get_or_create_role(guild: discord.Guild) -> discord.Role:
    """Fetch the activity role, creating it if it doesn't exist."""
    role = discord.utils.get(guild.roles, name=ACTIVITY_ROLE_NAME)
    if role is None:
        role = await guild.create_role(
            name=ACTIVITY_ROLE_NAME,
            colour=discord.Colour.gold(),
            reason="Auto-created for 7-day activity streak reward"
        )
        print(f"[INFO] Created role '{ACTIVITY_ROLE_NAME}' in {guild.name}")
    return role


# ---------------------------------------------------------------------------
# Rate limiting / slowmode (in-memory)
# ---------------------------------------------------------------------------
message_counts: Dict[str, list] = {}   # {channel_id: [datetime, ...]}


async def handle_dynamic_slowmode(channel: discord.TextChannel):
    if not isinstance(channel, discord.TextChannel):
        return

    now = datetime.now(timezone.utc)
    channel_id = str(channel.id)

    message_counts.setdefault(channel_id, [])

    # Keep only the last 2 minutes
    message_counts[channel_id] = [
        ts for ts in message_counts[channel_id]
        if now - ts < timedelta(minutes=2)
    ]
    message_counts[channel_id].append(now)

    count = len(message_counts[channel_id])

    # Thresholds: >30 msgs/2min → 5 min, >20 → 3 min, >10 → 1 min, else 0
    if count > 30:
        new_slowmode = 300
    elif count > 20:
        new_slowmode = 180
    elif count > 10:
        new_slowmode = 60
    else:
        new_slowmode = 0

    if channel.slowmode_delay != new_slowmode:
        try:
            await channel.edit(slowmode_delay=new_slowmode)
            if new_slowmode > 0:
                await channel.send(
                    f"🔒 Slowmode activated: {new_slowmode // 60} minute(s) due to high activity.",
                    delete_after=5,
                )
            else:
                await channel.send("✅ Chat has cooled down. Slowmode disabled.", delete_after=5)
        except discord.Forbidden:
            pass


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user.name} ({bot.user.id})')
    print('------')


@bot.event
async def on_member_join(member: discord.Member):
    # DM welcome
    try:
        await member.send(
            f"👋 Welcome to the server, **{member.name}**! "
            f"Glad to have you here. Please follow the rules and enjoy your stay!"
        )
    except discord.Forbidden:
        print(f"[WARN] Could not DM {member.name}")

    # Channel welcome
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        await channel.send(f"🎉 Welcome {member.mention} to the server! Say hi everyone!")
    else:
        print(f"[WARN] Welcome channel '{WELCOME_CHANNEL_NAME}' not found.")


@bot.event
async def on_message(message: discord.Message):
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Only process messages in guilds (not DMs)
    if not message.guild:
        return

    # ------------------------------------------------------------------
    # 1. Mention reply
    # ------------------------------------------------------------------
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        await message.reply(f"Hello {message.author.mention}! How can I help you today? 😊")

    # ------------------------------------------------------------------
    # 2. Profanity filter & strike system
    # ------------------------------------------------------------------
    content_lower = message.content.lower()
    if any(word in content_lower for word in BANNED_WORDS):
        await message.delete()

        strikes = load_strikes()
        user_id = str(message.author.id)
        current_strikes = strikes.get(user_id, 0) + 1
        strikes[user_id] = current_strikes
        save_strikes(strikes)

        if current_strikes >= 5:
            try:
                await message.guild.kick(
                    message.author, reason="Reached 5 strikes for profanity."
                )
                await message.channel.send(
                    f"🚫 **{message.author.name}** has been kicked for repeated profanity."
                )
                strikes.pop(user_id, None)
                save_strikes(strikes)
            except discord.Forbidden:
                await message.channel.send("⚠️ I don't have permission to kick this user.")
        else:
            await message.channel.send(
                f"⚠️ Warning {message.author.mention}! Profanity is not allowed. "
                f"You have **{current_strikes}/5** strikes.",
                delete_after=10,
            )
        # Don't process further if message was deleted
        return

    # ------------------------------------------------------------------
    # 3. 7-day activity streak → assign "Regular" role
    # ------------------------------------------------------------------
    user_id = str(message.author.id)
    streak = record_activity(user_id)

    if streak >= STREAK_DAYS_REQUIRED:
        role = await get_or_create_role(message.guild)
        if role not in message.author.roles:
            try:
                await message.author.add_roles(role, reason="7-day activity streak achieved!")
                await message.channel.send(
                    f"🌟 Congratulations {message.author.mention}! "
                    f"You've been active for **7 days straight** and earned the "
                    f"**{ACTIVITY_ROLE_NAME}** role!",
                    delete_after=30,
                )
            except discord.Forbidden:
                print(f"[WARN] Cannot assign role to {message.author.name} — missing permissions.")

    # ------------------------------------------------------------------
    # 4. Dynamic slowmode
    # ------------------------------------------------------------------
    await handle_dynamic_slowmode(message.channel)

    # Let commands work
    await bot.process_commands(message)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env file.")
    else:
        bot.run(TOKEN)
