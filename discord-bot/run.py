"""
Discord bot entry point.
Loads all command cogs and starts the bot.
"""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"[Bot] Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"[Bot] Connected to {len(bot.guilds)} server(s)")


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
