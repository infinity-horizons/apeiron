from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool
from apeiron.tools.discord.list_members import to_dict


class SearchMembersInput(BaseModel):
    """Arguments for searching Discord guild members."""

    query: str = Field(
        description="Optional search query to filter members by (case-insensitive)",
    )
    guild_id: int | None = Field(
        None, description="Discord guild (server) ID to search members in"
    )
    limit: int = Field(1000, description="Number of members to retrieve (max 100)")


class DiscordSearchMembersTool(BaseDiscordTool):
    """Tool for searching Discord guild members."""

    name: str = "search_members"
    description: str = "Search members in a Discord guild (server) by username"
    args_schema: type[SearchMembersInput] = SearchMembersInput

    async def _arun(
        self,
        query: str,
        guild_id: int | None = None,
        limit: int = 1000,
        config: RunnableConfig | None = None,
    ) -> list[dict]:
        """Search members in a guild with filters.

        Args:
            query: Optional search query to filter members by (case-insensitive).
            guild_id: The ID of the guild to search members in.
            limit: Number of members to retrieve (max 100).
            config: Optional runnable config object.

        Returns:
            List of member dictionaries matching the search criteria.
        """
        if guild_id is None and config:
            guild_id = config.get("configurable").get("guild_id")
        guild = await self.client.fetch_guild(guild_id)
        members = await guild.search_members(query=query, limit=limit)
        return [to_dict(member) for member in members]
