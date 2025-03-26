from discord import Client, Guild, Role
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field


def role_to_dict(role: Role) -> dict:
    """Convert role to dictionary representation."""
    return {
        "id": str(role.id),
        "name": role.name,
        "color": role.color.value,
        "position": role.position,
        "permissions": role.permissions.value,
        "hoist": role.hoist,
        "managed": role.managed,
        "mentionable": role.mentionable,
        "created_at": str(role.created_at),
    }


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
        "roles": [role_to_dict(role) for role in guild.roles],
    }


class GetGuildSchema(BaseModel):
    """Arguments for retrieving Discord guild information."""

    guild_id: str | None = Field(
        None, description="Discord guild (server) ID to look up"
    )


def create_get_guild_tool(client: Client):
    """Create a tool for retrieving Discord guild information."""

    @tool(
        name="get_guild",
        description="Get information about a Discord guild (server)",
        args_schema=GetGuildSchema,
    )
    async def get_guild(
        guild_id: str | None = None,
        config: RunnableConfig | None = None,
    ) -> dict:
        """Get guild information.

        Args:
            guild_id: The ID of the guild to retrieve information for.
            config: Optional RunnableConfig object.

        Returns:
            Dictionary representation of the guild.
        """
        if guild_id is None and config:
            guild_id = config.get("configurable").get("guild_id")
        try:
            guild = await client.fetch_guild(int(guild_id))
            return to_dict(guild)
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to get guild: {str(e)}") from e

    return get_guild
