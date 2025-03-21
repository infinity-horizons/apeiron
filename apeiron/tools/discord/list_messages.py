from discord import Message
from discord.errors import Forbidden, NotFound
from langchain_core.messages import ChatMessage
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


class ListMessagesSchema(BaseModel):
    """Arguments for listing Discord messages."""

    channel_id: int = Field(description="The ID of the channel to read messages from")
    before: str | None = Field(
        None, description="Optional message ID to read messages before"
    )
    after: str | None = Field(
        None, description="Optional message ID to read messages after"
    )
    limit: int = Field(100, description="Number of messages to retrieve (max 100)")


class DiscordListMessagesTool(BaseDiscordTool):
    name: str = "list_messages"
    description: str = "Read messages from a Discord channel with optional filters"
    args_schema: type[ListMessagesSchema] = ListMessagesSchema

    async def _arun(
        self,
        channel_id: int,
        before: str | None = None,
        after: str | None = None,
        limit: int = 100,
    ) -> list[ChatMessage]:
        try:
            channel = await self.client.fetch_channel(channel_id)
            kwargs = {"limit": limit}
            if before:
                kwargs["before"] = before
            if after:
                kwargs["after"] = after

            messages = []
            async for message in channel.history(**kwargs):
                messages.append(to_dict(message))
            return messages
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to read messages: {str(e)}") from e
