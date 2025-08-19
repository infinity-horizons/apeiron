from discord import Client, Emoji
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field


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


def create_get_emoji_tool(client: Client):
    """Create a tool for retrieving a specific Discord emoji."""

    @tool(args_schema=GetEmojiInput)
    async def get_emoji(
        emoji_id: int,
        guild_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> dict:
        """Get a specific emoji.

        Args:
            emoji_id: The ID of the emoji to retrieve.
            guild_id: The ID of the guild containing the emoji.
            config: Optional RunnableConfig object.

        Returns:
            Dictionary representation of the emoji.
        """
        if guild_id is None and config:
            guild_id = config.get("configurable").get("guild_id")
        try:
            guild = await client.fetch_guild(guild_id)
            emoji = await guild.fetch_emoji(emoji_id)
            return to_dict(emoji)
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to get emoji: {str(e)}") from e

    return get_emoji
