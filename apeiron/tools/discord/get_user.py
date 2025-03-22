from discord import Client, User
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


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


class DiscordGetUserInput(BaseModel):
    user_id: str = Field(description="Discord user ID to look up")


class DiscordGetUserTool(BaseTool):
    """Tool for retrieving Discord user profile information."""

    name = "user_profile"
    description = "Get information about a Discord user's profile"
    args_schema = DiscordGetUserInput

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

        async def _arun(self, user_id: str) -> dict:
            """Get user profile information."""
            user = await self.client.fetch_user(int(user_id))
            return to_dict(user)
