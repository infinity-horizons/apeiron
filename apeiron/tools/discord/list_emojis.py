from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool
from apeiron.tools.discord.get_emoji import to_dict


class ListEmojisSchema(BaseModel):
    """Arguments for listing Discord emojis."""

    guild_id: int = Field(description="The ID of the guild to list emojis from")


class DiscordListEmojisTool(BaseDiscordTool):
    """Tool for listing emojis in a Discord guild."""

    name: str = "list_emojis"
    description: str = "List all emojis in a Discord guild"
    args_schema: type[ListEmojisSchema] = ListEmojisSchema

    async def _arun(self, guild_id: int) -> list[dict]:
        """List all emojis in a Discord guild.

        Args:
            guild_id: The ID of the guild to list emojis from.

        Returns:
            A list of dictionaries containing emoji information.

        Raises:
            ToolException: If the emojis cannot be listed.
        """
        try:
            guild = await self.client.fetch_guild(guild_id)
            emojis = await guild.fetch_emojis()
            return [to_dict(emoji) for emoji in emojis]
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to list emojis: {str(e)}") from e
