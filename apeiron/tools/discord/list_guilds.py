from discord import Client
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from apeiron.tools.discord.get_guild import to_dict


class ListGuildsInput(BaseModel):
    """Arguments for listing Discord guilds."""

    before: str | None = Field(
        None, description="Optional guild ID to list guilds before"
    )
    after: str | None = Field(
        None, description="Optional guild ID to list guilds after"
    )
    limit: int = Field(100, description="Number of guilds to retrieve (max 100)")


def create_list_guilds_tool(client: Client):
    """Create a tool for listing Discord guilds the bot is a member of."""

    @tool(args_schema=ListGuildsInput)
    async def list_guilds(
        before: str | None = None,
        after: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """List all guilds with optional filters.

        Args:
            before: Optional guild ID to list guilds before.
            after: Optional guild ID to list guilds after.
            limit: Number of guilds to retrieve (max 100).

        Returns:
            List of guild dictionaries.
        """
        kwargs = {"limit": limit}
        if before:
            kwargs["before"] = before
        if after:
            kwargs["after"] = after

        guilds = await client.fetch_guilds(**kwargs).flatten()
        return [to_dict(guild) for guild in guilds]

    return list_guilds
