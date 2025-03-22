from discord import Message
from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


def to_dict(message: Message) -> dict:
    """Create message data structure."""
    attachments_data = []
    for attachment in message.attachments:
        attachment_info = {
            "filename": attachment.filename,
            "url": attachment.url,
            "size": attachment.size,
            "content_type": attachment.content_type,
        }
        if attachment.content_type and attachment.content_type.startswith("image/"):
            attachment_info.update(
                {
                    "type": "image",
                    "dimensions": {
                        "width": attachment.width,
                        "height": attachment.height,
                    },
                }
            )
        attachments_data.append(attachment_info)

    message_data = {
        "content": message.content,
        "id": str(message.id),
        "author": {
            "id": str(message.author.id),
            "name": message.author.name,
            "display_name": message.author.display_name,
            "bot": message.author.bot,
            "avatar_url": str(message.author.avatar.url)
            if message.author.avatar
            else None,
        },
        "channel_id": str(message.channel.id),
        "guild_id": str(message.guild.id) if message.guild else None,
        "timestamp": str(message.created_at),
        "edited_timestamp": str(message.edited_at) if message.edited_at else None,
        "attachments": attachments_data,
    }

    if message.reference and message.reference.resolved:
        ref = message.reference.resolved
        message_data["reference"] = {
            "id": str(ref.id),
            "content": ref.content,
            "author": str(ref.author),
            "timestamp": str(ref.created_at),
        }

    return message_data


class DiscordGetMessageInput(BaseModel):
    """Arguments for retrieving a specific Discord message."""

    channel_id: int = Field(description="The ID of the channel containing the message")
    message_id: int = Field(description="The ID of the message to retrieve")


class DiscordGetMessageTool(BaseDiscordTool):
    """Tool for retrieving a specific Discord message."""

    name: str = "get_message"
    description: str = "Get a specific message from a Discord channel"
    args_schema: type[DiscordGetMessageInput] = DiscordGetMessageInput

    async def _arun(self, channel_id: int, message_id: int) -> dict:
        """Get a specific message.

        Args:
            channel_id: The ID of the channel containing the message.
            message_id: The ID of the message to retrieve.

        Returns:
            Message data dictionary.

        Raises:
            ToolException: If there is an issue retrieving the message.
        """
        try:
            channel = await self.client.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            return to_dict(message)
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to get message: {str(e)}") from e
