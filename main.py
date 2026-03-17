import discord # type: ignore
from discord.ext import commands # type: ignore
import os
import json
from typing import Dict, List
from datetime import datetime, timedelta, timezone, date
from dotenv import load_dotenv # type: ignore

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WELCOME_CHANNEL_NAME = os.getenv('WELCOME_CHANNEL_NAME', 'general-discussion')

# Role name for members who are active 7 consecutive days
ACTIVITY_ROLE_NAME = "Regular"
STREAK_DAYS_REQUIRED = 7

# Server rules to be shown in welcome message
SERVER_RULES = [
    "✅ **Be respectful**: Treat all members with kindness and patience.",
    "✅ **No Harassment**: Zero tolerance for hate speech, bullying, or slurs.",
    "✅ **No Spamming**: Keep the channels clean and avoid excessive self-promotion.",
    "✅ **Semantic Channels**: Use the appropriate channels for your discussions.",
    "✅ **ToS Compliance**: Always follow Discord's official Terms of Service."
]

ARGUS_INTRO = [
    (
        "🛡️ **Argus Protocol — Full Introduction** 🛡️\n\n"
        "**What Is Argus Protocol?**\n"
        "Argus Protocol is the first self-healing, Zero-Ops infrastructure layer built on top of GhostDAG — the consensus mechanism that powers the Kaspa blockchain. "
        "It is an intelligent orchestration layer that sits between a raw GhostDAG node and the applications that depend on it — "
        "making that node behave like a system that thinks, repairs itself, and optimizes itself without human intervention.\n\n"
        "**The Problem It Solves**\n"
        "Running a GhostDAG node is hard. The consensus algorithm requires careful management of the k-parameter. "
        "If misconfigured, orphan rates climb and the node drifts. Argus eliminates this by managing:\n"
        "1️⃣ **Blue-set divergence**\n"
        "2️⃣ **Lag accumulation**\n"
        "3️⃣ **Peer isolation**"
    ),
    (
        "⚙️ **How It Works (The Engine)**\n\n"
        "**argus-agent**: The heart of Argus. A self-healing agent that detects drift or lag and triggers autonomous recovery without human touch.\n"
        "**argus-linearizer**: Flattens the 3D block DAG into a linear edge stream for AI agents and Graph Neural Networks (GNNs).\n"
        "**argus-optimizer**: Uses Proximal Policy Optimization (RL) to continuously observe orphan rates and automatically adjust the k-parameter.\n"
        "**argus-gateway**: A Zero-Ops API that exposes health reporting, DAG subgraph retrieval, and real-time event streams."
    ),
    (
        "💎 **Key Features & Status**\n\n"
        "🚀 **Zero-Ops**: Configure once, walk away. The agent handles failures autonomously.\n"
        "🧠 **Live Reinforcement Learning**: The PPO optimizer learns and improves k-parameter recommendations over time.\n"
        "📊 **Probabilistic Finality**: Provides a 0.0–1.0 confidence score for transaction finality.\n\n"
        "**Current Status:** Argus is open source and live! Next up: The Argus Meme Coin Launchpad (AGR token reward system).\n\n"
        "🔗 **Repository:** github.com/Fortunehack45/Argus-Synapse\n"
        "🌐 **Website:** argus-protocol.xyz"
    )
]

# ---------------------------------------------------------------------------
# Argus Knowledge Base (FAQ)
# ---------------------------------------------------------------------------
ARGUS_FAQ = {
    "what is": (
        "🛡️ **Argus Protocol** is a self-healing infrastructure layer built on top of GhostDAG (Kaspa). "
        "It acts as an intelligent orchestration layer that makes blockchain nodes think, repair, and optimize themselves automatically."
    ),
    "ghostdag": (
        "👻 **GhostDAG** is the consensus mechanism powering Kaspa. Unlike traditional chains, it maintains a directed acyclic graph (DAG) of blocks. "
        "Argus makes this complex system manageable for production use."
    ),
    "problem": (
        "🛠️ **Argus solves node drift, lag, and isolation.** It eliminates the need for manual intervention when orphan rates spike or nodes fall behind the network."
    ),
    "k-parameter": (
        "⚖️ The **k-parameter** controls the blue/red block classification in GhostDAG. Argus uses its **argus-optimizer** (Reinforcement Learning) "
        "to automatically adjust k based on live network conditions."
    ),
    "agent": (
        "🤖 The **argus-agent** is the self-healing heart of the protocol. It runs as a state machine that detects unhealthy nodes "
        "and triggers autonomous recovery procedures."
    ),
    "linearizer": (
        "📈 The **argus-linearizer** flattens the 3D block DAG into a linear edge stream. This allows AI agents and Graph Neural Networks (GNNs) "
        "to consume blockchain data in real-time."
    ),
    "optimizer": (
        "🧠 The **argus-optimizer** uses PPO (Proximal Policy Optimization) reinforcement learning to minimize orphan rates "
        "by intelligently tuning the network's k-parameter."
    ),
    "gateway": (
        "🌐 The **argus-gateway** provides a high-performance REST and WebSocket API for health reporting, finality scoring, and DAG analysis."
    ),
    "finality": (
        "🔍 Argus provides **Probabilistic Finality Scoring**. It translates complex DAG structure into a clear 0.0–1.0 confidence score for every transaction."
    ),
    "status": (
        "⚡ Argus is open source and live! The next major milestone is the **Argus Meme Coin Launchpad** using the AGR token system."
    ),
    "token": (
        "🪙 The native token of the Argus ecosystem is **AGR**, used for transactions and rewards within the upcoming Launchpad."
    ),
    "website": "🌐 Visit us at: https://argus-protocol.xyz",
    "github": "🔗 Repository: https://github.com/Fortunehack45/Argus-Synapse"
}


async def handle_argus_questions(message: discord.Message):
    content = message.content.lower()
    
    # Check for keywords and reply with relevant FAQ entry
    for key, answer in ARGUS_FAQ.items():
        if key in content:
            await message.reply(f"{answer}")
            return True
            
    # Default response if they mentioned argus but no specific keyword matched
    if "argus" in content:
        await message.reply(
            "I noticed you mentioned **Argus Protocol**! 🛡️\n"
            "You can ask me about: *what it is, how it works, the self-healing agent, k-parameter, the founder, token (AGR), or the website*."
        )
        return True
    return False

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

    # Lowered thresholds for better visibility and reactivity:
    # >5 msgs/2min -> 10s, >10 msgs -> 30s, >15 msgs -> 1m, >20 msgs -> 2m
    if count > 20:
        new_slowmode = 120
    elif count > 15:
        new_slowmode = 60
    elif count > 10:
        new_slowmode = 30
    elif count > 5:
        new_slowmode = 10
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
# Commands
# ---------------------------------------------------------------------------
@bot.command(name='role')
async def check_role(ctx: commands.Context):
    """Allows users to check their current roles."""
    roles = [role.name for role in ctx.author.roles if role.name != "@everyone"]
    if not roles:
        await ctx.reply("You don't have any specialized roles yet! Keep being active to earn the **Regular** role. 🚀")
    else:
        roles_list = ", ".join(roles)
        await ctx.reply(f"🛡️ **Your Roles:** {roles_list}")


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
        rules_text = "\n".join(SERVER_RULES)
        
        # 1. Official Welcome & Rules
        await channel.send(
            f"🎊 **WELCOME TO THE SERVER, {member.mention}!** 🎊\n"
            f"We are thrilled to have you here at the forefront of GhostDAG innovation! 🚀\n\n"
            f"📜 **COMMUNITY RULES:**\n{rules_text}\n\n"
            f"*Please take a moment to read our rules. Your presence here makes the network stronger!*"
        )
        
        # 2. Argus Protocol Introduction (in chunks)
        for chunk in ARGUS_INTRO:
            await channel.send(chunk)
            
        await channel.send(
            "--- \n"
            "🛡️ *The future of GhostDAG is self-healing. Enjoy your stay!* \n"
            "---"
        )
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

    # 1.5 Argus Q&A System
    # Check if the message is a question about Argus (either tags bot or mentions argus)
    if "argus" in message.content.lower() or bot.user.mentioned_in(message):
        # We only auto-reply to mentions or direct mentions of Argus to avoid being too spammy
        if await handle_argus_questions(message):
            return

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
                # DM before kick
                try:
                    await message.author.send(
                        f"🚫 You have been kicked from **{message.guild.name}** for reaching "
                        f"the maximum limit of 5 strikes for profanity."
                    )
                except discord.Forbidden:
                    pass

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
            strikes_left = 5 - current_strikes
            await message.channel.send(
                f"⚠️ Warning {message.author.mention}! Profanity is not allowed. "
                f"You have **{strikes_left}** strikes left before being kicked.",
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
                # DM notification
                try:
                    await message.author.send(
                        f"🎊 Congratulations! Your 7-day activity streak in **{message.guild.name}** "
                        f"has earned you the **{ACTIVITY_ROLE_NAME}** role. Keep up the great energy! 🚀"
                    )
                except discord.Forbidden:
                    pass # DM blocked
            except discord.Forbidden:
                print(f"[WARN] Cannot assign role to {message.author.name} — missing permissions.")

    # ------------------------------------------------------------------
    # 4. Dynamic slowmode
    # ------------------------------------------------------------------
    await handle_dynamic_slowmode(message.channel)

    # Let commands work
    await bot.process_commands(message)


import threading
from flask import Flask # type: ignore

app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is alive and running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    server = threading.Thread(target=run_flask)
    server.start()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN not found in .env file.")
    else:
        print("Starting web server...")
        keep_alive()
        print("Starting Discord bot...")
        bot.run(TOKEN)
