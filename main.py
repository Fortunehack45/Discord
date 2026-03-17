import discord
from discord.ext import commands
import os
import json
from typing import Dict
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WELCOME_CHANNEL_NAME = os.getenv('WELCOME_CHANNEL_NAME', 'general-discussion')

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Profanity list
BANNED_WORDS = ['shit', 'fuck', 'motherfucker', 'nigga', 'faggot'] # Common F-words and slurs

# Strike system storage
STRIKES_FILE = 'strikes.json'

def load_strikes() -> Dict[str, int]:
    if os.path.exists(STRIKES_FILE):
        with open(STRIKES_FILE, 'r') as f:
            data = json.load(f)
            return dict(data)
    return {}

def save_strikes(strikes: Dict[str, int]):
    with open(STRIKES_FILE, 'w') as f:
        json.dump(strikes, f, indent=4)

# Global for rate limiting logic
message_counts = {} # {channel_id: [timestamps]}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.event
async def on_member_join(member):
    # DM Welcome
    try:
        await member.send(f"Welcome to the server, {member.name}! Glad to have you here. Please follow the rules.")
    except discord.Forbidden:
        print(f"Could not DM {member.name}")

    # Channel Welcome
    channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL_NAME)
    if channel:
        await channel.send(f"Welcome {member.mention} to the server! Say hi everyone!")
    else:
        print(f"Welcome channel '{WELCOME_CHANNEL_NAME}' not found.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 1. Mention Reply
    if bot.user.mentioned_in(message) and not message.mention_everyone:
        await message.reply(f"Hello {message.author.mention}! How can I help you today?")

    # 2. Profanity Filter & Strike System
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
                await message.guild.kick(message.author, reason="Reached 5 strikes for profanity.")
                await message.channel.send(f"{message.author.name} has been kicked for repeated profanity.")
                strikes.pop(user_id, None) # Reset strikes after kick
                save_strikes(strikes)
            except discord.Forbidden:
                await message.channel.send("I don't have permission to kick this user.")
        else:
            await message.channel.send(f"Warning {message.author.mention}! Profanity is not allowed. You have {current_strikes}/5 strikes.", delete_after=10)

    # 3. Dynamic Rate Limiting (Slowmode)
    await handle_dynamic_slowmode(message.channel)

    await bot.process_commands(message)

async def handle_dynamic_slowmode(channel):
    if not isinstance(channel, discord.TextChannel):
        return

    now = datetime.now(timezone.utc)
    channel_id = str(channel.id)
    
    if channel_id not in message_counts:
        message_counts[channel_id] = []
    
    # Keep only last 2 minutes of timestamps
    message_counts[channel_id] = [ts for ts in message_counts[channel_id] if now - ts < timedelta(minutes=2)]
    message_counts[channel_id].append(now)

    count = len(message_counts[channel_id])
    
    # 1 to 5 minutes gap depending on how many people is typing
    # Let's say: 
    # > 10 msgs/2min -> 1 min slowmode
    # > 20 msgs/2min -> 3 min slowmode
    # > 30 msgs/2min -> 5 min slowmode
    
    new_slowmode = 0
    if count > 30:
        new_slowmode = 300 # 5 minutes
    elif count > 20:
        new_slowmode = 180 # 3 minutes
    elif count > 10:
        new_slowmode = 60 # 1 minute
    
    if channel.slowmode_delay != new_slowmode:
        try:
            await channel.edit(slowmode_delay=new_slowmode)
            if new_slowmode > 0:
                await channel.send(f"🔒 Slowmode activated: {new_slowmode//60} minute(s) due to high activity.", delete_after=5)
            else:
                await channel.send("Chat has cooled down. Slowmode disabled.", delete_after=5)
        except discord.Forbidden:
            pass

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in .env file.")
    else:
        bot.run(TOKEN)
