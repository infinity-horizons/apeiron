from discord import Member
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


def to_dict(member: Member) -> dict:
    """Convert member to dictionary representation."""
    return {
        "id": str(member.id),
        "name": member.name,
        "display_name": member.display_name,
        "bot": member.bot,
        "roles": [str(role.id) for role in member.roles],
        "joined_at": str(member.joined_at) if member.joined_at else None,
        "premium_since": str(member.premium_since) if member.premium_since else None,
        "pending": member.pending,
        "nick": member.nick,
        "avatar_url": str(member.avatar.url) if member.avatar else None,
    }


class ListMembersInput(BaseModel):
    """Arguments for listing Discord guild members."""

    guild_id: str = Field(description="Discord guild (server) ID to list members from")
    before: str | None = Field(
        None, description="Optional member ID to list members before"
    )
    after: str | None = Field(
        None, description="Optional member ID to list members after"
    )
    limit: int = Field(100, description="Number of members to retrieve (max 100)")


class DiscordListMembersTool(BaseDiscordTool):
    """Tool for listing Discord guild members."""

    name: str = "list_members"
    description: str = "List all members in a Discord guild (server)"
    args_schema: type[ListMembersInput] = ListMembersInput

    async def _arun(
        self,
        guild_id: str,
        before: str | None = None,
        after: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """List members in a guild with optional filters.

        Args:
            guild_id: The ID of the guild to list members from.
            before: Optional member ID to list members before.
            after: Optional member ID to list members after.
            limit: Number of members to retrieve (max 100).

        Returns:
            List of member dictionaries.
        """
        guild = await self.client.fetch_guild(int(guild_id))
        kwargs = {"limit": limit}
        if before:
            kwargs["before"] = before
        if after:
            kwargs["after"] = after

        members = await guild.fetch_members(**kwargs).flatten()
        return [to_dict(member) for member in members]
