from discord import TextChannel
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


def to_dict(channel: TextChannel) -> dict:
    """Convert channel to dictionary representation."""
    return {
        "id": str(channel.id),
        "name": channel.name,
        "type": str(channel.type),
        "position": channel.position,
        "category_id": str(channel.category_id) if channel.category_id else None,
        "topic": channel.topic if hasattr(channel, "topic") else None,
        "nsfw": channel.nsfw if hasattr(channel, "nsfw") else None,
        "created_at": str(channel.created_at),
        "parent_id": str(channel.parent_id) if channel.parent_id else None,
    }


class DiscordListChannelsInput(BaseModel):
    guild_id: int = Field(description="Discord guild (server) ID to list channels from")


class DiscordListChannelsTool(BaseDiscordTool):
    """Tool for listing Discord channels in a guild."""

    name: str = "list_channels"
    description: str = "List all channels in a Discord guild (server)"
    args_schema: type[DiscordListChannelsInput] = DiscordListChannelsInput

    async def _arun(self, guild_id: int) -> list[dict]:
        """List channels in a guild."""
        guild = await self.client.fetch_guild(guild_id)
        channels = await guild.fetch_channels()
        return [to_dict(channel) for channel in channels]
