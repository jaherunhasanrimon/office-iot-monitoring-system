"""!room <name> — single room summary."""

from discord.ext import commands
from ..services import api_client, llm_formatter


class RoomCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="room")
    async def room(self, ctx, *, room_name: str | None = None):
        """Show status for a specific room. Usage: !room work1"""
        if not room_name:
            await ctx.send("Usage: `!room <name>` — e.g., `!room work1` or `!room drawing`")
            return

        async with ctx.typing():
            room = api_client.get(f"/api/rooms/{room_name.strip()}")
            if room is None:
                await ctx.send(
                    f"⚠️ Room **{room_name}** not found. "
                    f"Try: `drawing`, `work1`, or `work2`."
                )
                return
            if not isinstance(room, dict):
                await ctx.send(f"⚠️ Unexpected response format for room **{room_name}**.")
                return
            reply = llm_formatter.format_room(room)
        await ctx.send(reply)


async def setup(bot):
    await bot.add_cog(RoomCog(bot))
