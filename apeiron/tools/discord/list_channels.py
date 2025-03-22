from discord import Client, TextChannel
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


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
    guild_id: str = Field(description="Discord guild (server) ID to list channels from")


class DiscordListChannelsTool(BaseTool):
    """Tool for listing Discord channels in a guild."""

    name = "list_channels"
    description = "List all channels in a Discord guild (server)"
    args_schema = DiscordListChannelsInput

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    async def _arun(self, guild_id: str) -> list[dict]:
        """List channels in a guild."""
        guild = await self.client.fetch_guild(int(guild_id))
        channels = await guild.fetch_channels()
        return [to_dict(channel) for channel in channels]
