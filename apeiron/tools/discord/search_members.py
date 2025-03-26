from discord import Client
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.list_members import to_dict


class SearchMembersSchema(BaseModel):
    """Arguments for searching Discord guild members."""

    query: str = Field(
        description="Optional search query to filter members by (case-insensitive)",
    )
    guild_id: int | None = Field(
        None, description="Discord guild (server) ID to search members in"
    )
    limit: int = Field(1000, description="Number of members to retrieve (max 100)")


def create_search_members_tool(client: Client):
    """Create a tool for searching Discord guild members."""

    @tool(
        name="search_members",
        description="Search members in a Discord guild (server) by username",
        args_schema=SearchMembersSchema,
    )
    async def search_members(
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

        Raises:
            ToolException: If the members cannot be searched.
        """
        if guild_id is None and config:
            guild_id = config.get("configurable").get("guild_id")
        try:
            guild = await client.fetch_guild(guild_id)
            members = await guild.search_members(query=query, limit=limit)
            return [to_dict(member) for member in members]
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to search members: {str(e)}") from e

    return search_members
