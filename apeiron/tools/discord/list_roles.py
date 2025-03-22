from discord import Role
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


def to_dict(role: Role) -> dict:
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


class ListRolesInput(BaseModel):
    """Input for the DiscordListRolesTool."""

    guild_id: str = Field(description="Discord guild (server) ID to list roles from")


class DiscordListRolesTool(BaseDiscordTool):
    """Tool for listing Discord roles in a guild."""

    name: str = "list_roles"
    description: str = "List all roles in a Discord guild (server)"
    args_schema: type[ListRolesInput] = ListRolesInput

    async def _arun(self, guild_id: str) -> list[dict]:
        """List roles in a guild.

        Args:
            guild_id: The ID of the guild to list roles from.

        Returns:
            List of role dictionaries.
        """
        guild = await self.client.fetch_guild(int(guild_id))
        roles = guild.roles
        return [to_dict(role) for role in roles]