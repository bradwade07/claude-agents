import os
import discord
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .agent import bradbot_chat, _start_file_watcher

load_dotenv("secrets/.env")

DISCORD_TOKEN = os.getenv("BRADBOT_DISCORD_TOKEN")
SERVER_ID = int(os.getenv("BRADBOT_SERVER_ID") or "0")
DISPATCH_CHANNEL_ID = int(os.getenv("BRADBOT_DISPATCH_CHANNEL_ID") or "0")
BRIEFING_CHANNEL_ID = int(os.getenv("BRADBOT_BRIEFING_CHANNEL_ID") or "0")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
scheduler = None


@client.event
async def on_ready():
    """Bot is ready."""
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler(timezone="America/Chicago")
        scheduler.add_job(morning_briefing, "cron", hour=8, minute=0)
        scheduler.start()
    _start_file_watcher()
    print(f"Bradbot ready. Logged in as {client.user}")


@client.event
async def on_message(message):
    """Handle incoming messages in dispatch channel."""
    if message.author.bot:
        return
    if message.guild.id != SERVER_ID:
        return
    if message.channel.id != DISPATCH_CHANNEL_ID:
        return

    async with message.channel.typing():
        reply = await bradbot_chat(message.content)

    await message.channel.send(reply)


async def morning_briefing():
    """Post morning briefing at 8am in briefing channel."""
    if not BRIEFING_CHANNEL_ID:
        print("Briefing disabled (BRADBOT_BRIEFING_CHANNEL_ID not set)")
        return
    try:
        channel = client.get_channel(BRIEFING_CHANNEL_ID) or await client.fetch_channel(BRIEFING_CHANNEL_ID)
        briefing_prompt = (
            "Give me my daily briefing: today's calendar events, open ClickUp tasks, "
            "and anything important from my notes."
        )
        reply = await bradbot_chat(briefing_prompt)
        await channel.send(reply)
    except Exception as e:
        print(f"Error sending morning briefing: {e}")


def run():
    """Start the bot."""
    if not DISCORD_TOKEN:
        raise ValueError("BRADBOT_DISCORD_TOKEN not set in secrets/.env")
    if SERVER_ID == 0:
        raise ValueError("BRADBOT_SERVER_ID not set in secrets/.env")
    if DISPATCH_CHANNEL_ID == 0:
        raise ValueError("BRADBOT_DISPATCH_CHANNEL_ID not set in secrets/.env")
    if BRIEFING_CHANNEL_ID == 0:
        print("Warning: BRADBOT_BRIEFING_CHANNEL_ID not set — morning briefings disabled")

    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run()
