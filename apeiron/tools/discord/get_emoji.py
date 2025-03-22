from discord import Emoji
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
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


class GetEmojiInput(BaseModel):
    """Arguments for retrieving a specific Discord emoji."""

    emoji_id: int = Field(description="The ID of the emoji to retrieve")
    guild_id: int | None = Field(
        None, description="The ID of the guild containing the emoji"
    )


class DiscordGetEmojiTool(BaseDiscordTool):
    """Tool for retrieving a specific Discord emoji."""

    name: str = "get_emoji"
    description: str = "Get a specific emoji from a Discord guild"
    args_schema: type[GetEmojiInput] = GetEmojiInput

    async def _arun(
        self, emoji_id: int, guild_id: int, config: RunnableConfig | None = None
    ) -> dict:
        """Get a specific emoji.

        Args:
            guild_id: The ID of the guild containing the emoji.
            emoji_id: The ID of the emoji to retrieve.
            config: Optional RunnableConfig object.

        Returns:
            Dictionary representation of the emoji.
        """
        if guild_id is None and config:
            guild_id = config.configurable.get("guild_id")
        try:
            guild = await self.client.fetch_guild(guild_id)
            emoji = await guild.fetch_emoji(emoji_id)
            return to_dict(emoji)
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to get emoji: {str(e)}") from e
