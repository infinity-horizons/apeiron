from discord import Message
from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


def attachment_to_dict(attachment) -> dict:
    """Convert attachment to dictionary representation."""
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
    return attachment_info


def author_to_dict(author) -> dict:
    """Convert author to dictionary representation."""
    return {
        "id": str(author.id),
        "name": author.name,
        "display_name": author.display_name,
        "bot": author.bot,
        "avatar_url": str(author.avatar.url) if author.avatar else None,
    }


def reference_to_dict(reference) -> dict:
    """Convert message reference to dictionary representation."""
    ref = reference.resolved
    return {
        "id": str(ref.id),
        "content": ref.content,
        "author": str(ref.author),
        "timestamp": str(ref.created_at),
    }


def to_dict(message: Message) -> dict:
    """Create message data structure."""
    message_data = {
        "content": message.content,
        "id": str(message.id),
        "author": author_to_dict(message.author),
        "channel_id": str(message.channel.id),
        "guild_id": str(message.guild.id) if message.guild else None,
        "timestamp": str(message.created_at),
        "edited_timestamp": str(message.edited_at) if message.edited_at else None,
        "attachments": [attachment_to_dict(attachment) for attachment in message.attachments],
    }

    if message.reference and message.reference.resolved:
        message_data["reference"] = reference_to_dict(message.reference)

    return message_data


class GetMessageInput(BaseModel):
    """Arguments for retrieving a specific Discord message."""

    channel_id: int = Field(description="The ID of the channel containing the message")
    message_id: int = Field(description="The ID of the message to retrieve")


class DiscordGetMessageTool(BaseDiscordTool):
    """Tool for retrieving a specific Discord message."""

    name: str = "get_message"
    description: str = "Get a specific message from a Discord channel"
    args_schema: type[GetMessageInput] = GetMessageInput

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
