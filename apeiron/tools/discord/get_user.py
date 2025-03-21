from discord import Client
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class GetUserInput(BaseModel):
    user_id: str = Field(description="Discord user ID to look up")


class GetUserTool(BaseTool):
    """Tool for retrieving Discord user profile information."""

    name = "user_profile"
    description = "Get information about a Discord user's profile"
    args_schema = GetUserInput

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    async def _arun(self, user_id: str) -> dict:
        """Get user profile information."""
        user = await self.client.fetch_user(int(user_id))
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
