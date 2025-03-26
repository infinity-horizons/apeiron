from discord import TextChannel, Client
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools.base import ToolException
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from apeiron.tools.discord.list_channels import to_dict


class GetChannelSchema(BaseModel):
    """Arguments for retrieving a specific Discord channel."""

    channel_id: int | None = Field(
        None, description="The ID of the channel to retrieve"
    )


def create_get_channel_tool(client: Client):
    """Create a tool for retrieving a specific Discord channel."""

    @tool(name="get_channel", description="Get a specific channel from Discord", args_schema=GetChannelSchema)
    async def get_channel(
        channel_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> dict:
        """Get channel information.

        Args:
            channel_id: The ID of the channel to retrieve.
            config: Optional RunnableConfig object.

        Returns:
            The channel information.

        Raises:
            ToolException: If the channel is not found or not a text channel.
        """
        if channel_id is None and config:
            channel_id = config.get("configurable").get("channel_id")
        try:
            channel = await client.fetch_channel(channel_id)
            if not isinstance(channel, TextChannel):
                raise ToolException(
                    f"Channel {channel_id} not found or not a text channel"
                )
            return to_dict(channel)
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to get channel: {str(e)}") from e

    return get_channel
