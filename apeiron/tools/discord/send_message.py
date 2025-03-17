from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


class SendMessageSchema(BaseModel):
    """Arguments for sending Discord messages."""

    content: str = Field(description="The content of the message to send")
    channel_id: int = Field(description="ID of the channel to send the message to")


class DiscordSendMessageTool(BaseDiscordTool):
    """Tool for sending messages to a Discord channel."""

    name: str = "send_message"
    description: str = "Send a message to a Discord channel"
    args_schema: type[SendMessageSchema] = SendMessageSchema

    async def _arun(
        self,
        content: str,
        channel_id: int,
    ) -> str:
        """Send a message to a Discord channel.

        Args:
            content: The content of the message to send
            channel_id: ID of the channel to send the message to

        Returns:
            str: Confirmation message with the sent message ID
        """
        try:
            channel = await self.client.fetch_channel(channel_id)
            if not channel:
                raise ToolException(f"Channel {channel_id} not found")
            message = await channel.send(content)
            return f"Message sent successfully with ID: {message.id}"
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to send message: {str(e)}") from e
