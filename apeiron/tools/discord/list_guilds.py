from langchain.tools import BaseTool
from pydantic import BaseModel

from apeiron.tools.discord.get_guild import to_dict


class DiscordListGuildsTool(BaseTool):
    """Tool for listing Discord guilds the bot is a member of."""

    name = "list_guilds"
    description = "List all Discord guilds (servers) the bot is a member of"
    args_schema = BaseModel

    async def _arun(self) -> list[dict]:
        """List all guilds."""
        guilds = await self.client.fetch_guilds().flatten()
        return [to_dict(guild) for guild in guilds]
