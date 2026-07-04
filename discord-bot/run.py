import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from bot.services import api_client

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Track alert IDs that have already been notified to prevent duplicate messages
sent_alert_ids = set()


@tasks.loop(seconds=15)
async def poll_alerts():
    channel_id = os.getenv("DISCORD_ALERT_CHANNEL_ID")
    if not channel_id or "placeholder" in channel_id:
        return

    try:
        channel_id = int(channel_id)
    except ValueError:
        return

    if not bot.is_ready():
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        return

    alerts = api_client.get("/api/alerts")
    if not alerts:
        return

    for alert in alerts:
        alert_id = alert.get("id")
        # Check if alert is unresolved (active) and hasn't been posted yet
        if alert_id not in sent_alert_ids and not alert.get("resolved_at"):
            sent_alert_ids.add(alert_id)
            badge = "🌙 AFTER HOURS" if alert["type"] == "after_hours" else "⏰ PROLONGED ON"
            msg = f"🚨 **{badge} ALERT**\n{alert['message']}"
            await channel.send(msg)


@bot.event
async def on_ready():
    print(f"[Bot] Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"[Bot] Connected to {len(bot.guilds)} server(s)")
    if not poll_alerts.is_running():
        poll_alerts.start()
        print("[Bot] Started alert polling loop.")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"⚠️ Error: {error}")


async def main():
    async with bot:
        await bot.load_extension("bot.commands.status")
        await bot.load_extension("bot.commands.room")
        await bot.load_extension("bot.commands.usage")
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("DISCORD_TOKEN is not set in .env")
        await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

