from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool
from apeiron.tools.discord.list_members import to_dict


class SearchMembersInput(BaseModel):
    """Arguments for searching Discord guild members."""

    guild_id: str = Field(description="Discord guild (server) ID to search members in")
    query: str | None = Field(
        None,
        description="Optional search query to filter members by (case-insensitive)",
    )
    limit: int | None = Field(description="Number of members to retrieve (max 100)")


class DiscordSearchMembersTool(BaseDiscordTool):
    """Tool for searching Discord guild members."""

    name: str = "search_members"
    description: str = "Search members in a Discord guild (server) by username"
    args_schema: type[SearchMembersInput] = SearchMembersInput

    async def _arun(
        self,
        guild_id: str,
        query: str | None = None,
        limit: int = 1000,
    ) -> list[dict]:
        """Search members in a guild with filters.

        Args:
            guild_id: The ID of the guild to search members in.
            query: Optional search query to filter members by (case-insensitive).
            limit: Number of members to retrieve (max 100).

        Returns:
            List of member dictionaries matching the search criteria.
        """
        guild = await self.client.fetch_guild(int(guild_id))
        members = await guild.search_members(query=query, limit=limit)
        return [to_dict(member) for member in members]
