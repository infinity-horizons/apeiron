from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


class ReplyMessageSchema(BaseModel):
    """Arguments for replying to Discord messages."""

    content: str | None = Field(None, description="The content of the reply message")
    message_id: int | None = Field(None, description="ID of the message to reply to")
    channel_id: int | None = Field(
        None, description="ID of the channel containing the message"
    )


class DiscordReplyMessageTool(BaseDiscordTool):
    """Tool for replying to messages in a Discord channel."""

    name: str = "reply_message"
    description: str = "Reply to a message in a Discord channel"
    args_schema: type[ReplyMessageSchema] = ReplyMessageSchema

    async def _arun(
        self,
        content: str | None = None,
        message_id: int | None = None,
        channel_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> str:
        """Reply to a message in a Discord channel.

        Args:
            content: The content of the reply message.
            message_id: Optional ID of the message to reply to.
            channel_id: Optional ID of the channel containing the message.
            config: Optional RunnableConfig object.

        Returns:
            Confirmation message with the reply ID.

        Raises:
            ToolException: If there is an issue sending the reply.
        """
        if not message_id and config:
            message_id = config.configurable.get("message_id")
        try:
            channel = await self.client.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            message = await message.reply(content)
            return f"Reply sent successfully with ID: {message.id}"
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to send reply: {str(e)}") from e
