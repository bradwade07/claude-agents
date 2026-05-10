import os
import discord
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .agent import bradbot_chat

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BRAD_USER_ID = int(os.getenv("DISCORD_USER_ID", "0"))

client = discord.Client(intents=discord.Intents.default())
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
    """Handle incoming messages."""
    if message.author.id != BRAD_USER_ID:
        return
    if not isinstance(message.channel, discord.DMChannel):
        return

    async with message.channel.typing():
        reply = await bradbot_chat(message.content)

    await message.channel.send(reply)


async def morning_briefing():
    """Send morning briefing at 8am."""
    try:
        user = await client.fetch_user(BRAD_USER_ID)
        dm = await user.create_dm()

        briefing_prompt = (
            "Give me my daily briefing: today's calendar events, open ClickUp tasks, "
            "and anything important from my notes."
        )
        reply = await bradbot_chat(briefing_prompt)
        await dm.send(reply)
    except Exception as e:
        print(f"Error sending morning briefing: {e}")


def run():
    """Start the bot."""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN not set in .env")
    if BRAD_USER_ID == 0:
        raise ValueError("DISCORD_USER_ID not set in .env")

    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    run()
