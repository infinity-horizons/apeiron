from discord import User
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


def to_dict(user: User) -> dict:
    """Convert user to dictionary representation."""
    return {
        "id": str(user.id),
        "name": user.name,
        "display_name": user.display_name,
        "bot": user.bot,
        "created_at": str(user.created_at),
        "avatar_url": str(user.avatar.url) if user.avatar else None,
        "banner_url": str(user.banner.url) if user.banner else None,
        "accent_color": str(user.accent_color) if user.accent_color else None,
    }


class GetUserInput(BaseModel):
    user_id: int | None = Field(None, description="Discord user ID to look up")


class DiscordGetUserTool(BaseDiscordTool):
    """Tool for retrieving Discord user profile information."""

    name: str = "user_profile"
    description: str = "Get information about a Discord user's profile"
    args_schema: type[GetUserInput] = GetUserInput

    async def _arun(
        self, user_id: int | None = None, config: RunnableConfig | None = None
    ) -> dict:
        """Get user profile information.

        Args:
            user_id: The ID of the user to look up.
            config: Optional RunnableConfig object.

        Returns:
            Dictionary containing user information.
        """
        if user_id is None and config:
            user_id = config.get("configurable").get("user_id")
        user = await self.client.fetch_user(user_id)
        return to_dict(user)
