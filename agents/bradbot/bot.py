import os
import discord
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .agent import bradbot_chat

load_dotenv("secrets/.env")

DISCORD_TOKEN = os.getenv("BRADBOT_DISCORD_TOKEN")
BRADBOT_CHANNEL_ID = int(os.getenv("BRADBOT_CHANNEL_ID") or "0")

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
    print(f"Bradbot ready. Logged in as {client.user}")


@client.event
async def on_message(message):
    """Handle incoming messages, scoped to one channel only."""
    if message.author.bot:
        return
    if message.channel.id != BRADBOT_CHANNEL_ID:
        return

    async with message.channel.typing():
        reply = await bradbot_chat(message.content)

    await message.channel.send(reply)


async def morning_briefing():
    """Post morning briefing at 8am in the configured channel."""
    try:
        channel = client.get_channel(BRADBOT_CHANNEL_ID) or await client.fetch_channel(BRADBOT_CHANNEL_ID)
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
    if BRADBOT_CHANNEL_ID == 0:
        raise ValueError("BRADBOT_CHANNEL_ID not set in secrets/.env")

    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run()
