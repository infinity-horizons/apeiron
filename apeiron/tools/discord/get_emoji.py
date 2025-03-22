from discord import Emoji
from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


def to_dict(emoji: Emoji) -> dict:
    """Convert emoji to dictionary representation."""
    return {
        "id": emoji.id,
        "name": emoji.name,
        "animated": emoji.animated,
        "available": emoji.available,
        "managed": emoji.managed,
        "require_colons": emoji.require_colons,
        "url": str(emoji.url),
        "created_at": str(emoji.created_at),
        "guild_id": str(emoji.guild_id),
    }


class DiscordGetEmojiInput(BaseModel):
    guild_id: int = Field(description="The ID of the guild containing the emoji")
    emoji_id: int = Field(description="The ID of the emoji to retrieve")


class DiscordGetEmojiTool(BaseDiscordTool):
    """Tool for retrieving a specific Discord emoji."""

    name = "get_emoji"
    description = "Get a specific emoji from a Discord guild"
    args_schema = DiscordGetEmojiInput

    async def _arun(self, guild_id: int, emoji_id: int) -> dict:
        """Get a specific emoji."""
        try:
            guild = await self.client.fetch_guild(guild_id)
            emoji = await guild.fetch_emoji(emoji_id)
            return to_dict(emoji)
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to get emoji: {str(e)}") from e
