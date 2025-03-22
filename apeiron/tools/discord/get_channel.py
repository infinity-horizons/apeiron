from discord import TextChannel
from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool
from apeiron.tools.discord.list_channels import to_dict


class GetChannelInput(BaseModel):
    """Arguments for retrieving a specific Discord channel."""

    channel_id: int = Field(description="The ID of the channel to retrieve")


class DiscordGetChannelTool(BaseDiscordTool):
    """Tool for retrieving a specific Discord channel."""

    name: str = "get_channel"
    description: str = "Get a specific channel from Discord"
    args_schema: type[GetChannelInput] = GetChannelInput

    async def _arun(self, channel_id: int) -> dict:
        """Get channel information.

        Args:
            channel_id: The ID of the channel to retrieve.

        Returns:
            The channel information.

        Raises:
            ToolException: If the channel is not found or not a text channel.
        """
        try:
            channel = await self.client.fetch_channel(channel_id)
            if not isinstance(channel, TextChannel):
                raise ToolException(
                    f"Channel {channel_id} not found or not a text channel"
                )
            return to_dict(channel)
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to get channel: {str(e)}") from e
