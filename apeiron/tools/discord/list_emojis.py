from discord import Client
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools.base import ToolException
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from apeiron.tools.discord.get_emoji import to_dict


class ListEmojisSchema(BaseModel):
    """Arguments for listing Discord emojis."""

    guild_id: int | None = Field(
        None, description="The ID of the guild to list emojis from"
    )


def create_list_emojis_tool(client: Client):
    """Create a tool for listing emojis in a Discord guild."""

    @tool(name="list_emojis", description="List all emojis in a Discord guild", args_schema=ListEmojisSchema)
    async def list_emojis(
        guild_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> list[dict]:
        """List all emojis in a Discord guild.

        Args:
            guild_id: The ID of the guild to list emojis from.
            config: Optional RunnableConfig object.

        Returns:
            A list of dictionaries containing emoji information.

        Raises:
            ToolException: If the emojis cannot be listed.
        """
        if guild_id is None and config:
            guild_id = config.get("configurable").get("guild_id")
        try:
            guild = await client.fetch_guild(guild_id)
            emojis = await guild.fetch_emojis()
            return [to_dict(emoji) for emoji in emojis]
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to list emojis: {str(e)}") from e

    return list_emojis
