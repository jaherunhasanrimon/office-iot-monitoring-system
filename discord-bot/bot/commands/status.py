"""!status — full office summary."""

from discord.ext import commands
from ..services import api_client, llm_formatter


class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    async def status(self, ctx):
        """Show the status of all devices in all rooms."""
        async with ctx.typing():
            rooms = api_client.get("/api/rooms")
            if rooms is None:
                await ctx.send("⚠️ Could not reach the backend. Please try again.")
                return
            if not isinstance(rooms, list):
                await ctx.send("⚠️ Unexpected response format from the backend.")
                return
            reply = llm_formatter.format_status(rooms)
        await ctx.send(reply)


async def setup(bot):
    await bot.add_cog(StatusCog(bot))
