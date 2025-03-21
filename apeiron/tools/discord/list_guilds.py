from pydantic import BaseModel

from apeiron.tools.discord.base import BaseDiscordTool
from apeiron.tools.discord.get_guild import to_dict


class DiscordListGuildsTool(BaseDiscordTool):
    """Tool for listing Discord guilds the bot is a member of."""

    name: str = "list_guilds"
    description: str = "List all Discord guilds (servers) the bot is a member of"
    args_schema: type[BaseModel] = BaseModel

    async def _arun(self) -> list[dict]:
        """List all guilds.

        Returns:
            List of guild dictionaries.
        """
        guilds = await self.client.fetch_guilds().flatten()
        return [to_dict(guild) for guild in guilds]
