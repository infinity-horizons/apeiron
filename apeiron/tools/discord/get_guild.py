from discord import Guild
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


def to_dict(guild: Guild) -> dict:
    """Convert guild to dictionary representation."""
    return {
        "id": str(guild.id),
        "name": guild.name,
        "description": guild.description,
        "owner_id": str(guild.owner_id),
        "member_count": guild.member_count,
        "icon_url": str(guild.icon.url) if guild.icon else None,
        "banner_url": str(guild.banner.url) if guild.banner else None,
        "created_at": str(guild.created_at),
        "premium_tier": guild.premium_tier,
        "premium_subscription_count": guild.premium_subscription_count,
    }


class GetGuildInput(BaseModel):
    """Arguments for retrieving Discord guild information."""

    guild_id: str = Field(description="Discord guild (server) ID to look up")


class DiscordGetGuildTool(BaseDiscordTool):
    """Tool for retrieving Discord guild information."""

    name: str = "get_guild"
    description: str = "Get information about a Discord guild (server)"
    args_schema: type[GetGuildInput] = GetGuildInput

    async def _arun(self, guild_id: str) -> dict:
        """Get guild information.

        Args:
            guild_id: The ID of the guild to retrieve information for.

        Returns:
            Dictionary representation of the guild.
        """
        guild = await self.client.fetch_guild(int(guild_id))
        return to_dict(guild)
