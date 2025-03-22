from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool
from apeiron.tools.discord.get_guild import to_dict


class ListGuildsSchema(BaseModel):
    """Arguments for listing Discord guilds."""

    before: str | None = Field(
        None, description="Optional guild ID to list guilds before"
    )
    after: str | None = Field(
        None, description="Optional guild ID to list guilds after"
    )
    limit: int = Field(100, description="Number of guilds to retrieve (max 100)")


class DiscordListGuildsTool(BaseDiscordTool):
    """Tool for listing Discord guilds the bot is a member of."""

    name: str = "list_guilds"
    description: str = "List all Discord guilds (servers) the bot is a member of"
    args_schema: type[ListGuildsSchema] = ListGuildsSchema

    async def _arun(
        self,
        before: str | None = None,
        after: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """List all guilds with optional filters.

        Args:
            before: Optional guild ID to list guilds before.
            after: Optional guild ID to list guilds after.
            limit: Number of guilds to retrieve (max 100).
            config: Optional RunnableConfig object.

        Returns:
            List of guild dictionaries.
        """
        kwargs = {"limit": limit}
        if before:
            kwargs["before"] = before
        if after:
            kwargs["after"] = after

        guilds = await self.client.fetch_guilds(**kwargs).flatten()
        return [to_dict(guild) for guild in guilds]
