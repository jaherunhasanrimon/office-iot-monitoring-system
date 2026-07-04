"""!usage — current wattage + today's estimated kWh."""

from discord.ext import commands
from ..services import api_client, llm_formatter


class UsageCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="usage")
    async def usage(self, ctx):
        """Show current power draw and today's estimated kWh usage."""
        async with ctx.typing():
            current = api_client.get("/api/usage/current")
            today = api_client.get("/api/usage/today")
            if current is None or today is None:
                await ctx.send("⚠️ Could not reach the backend. Please try again.")
                return
            if not isinstance(current, dict) or not isinstance(today, dict):
                await ctx.send("⚠️ Unexpected data format from the backend.")
                return
            reply = llm_formatter.format_usage(current, today)
        await ctx.send(reply)


async def setup(bot):
    await bot.add_cog(UsageCog(bot))
