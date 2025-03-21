from discord import Embed, File, MessageReference
from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


class SendMessageSchema(BaseModel):
    """Arguments for sending Discord messages."""

    content: str | None = Field(None, description="The content of the message to send")
    channel_id: int = Field(description="ID of the channel to send the message to")
    tts: bool = Field(False, description="Whether to send as text-to-speech message")
    embeds: list[dict] | None = Field(None, description="List of embed dictionaries")
    files: list[str] | None = Field(None, description="List of file paths to send")
    reference: int | None = Field(None, description="Message ID to reply to")


class DiscordSendMessageTool(BaseDiscordTool):
    """Tool for sending messages to a Discord channel."""

    name: str = "send_message"
    description: str = "Send a message to a Discord channel"
    args_schema: type[SendMessageSchema] = SendMessageSchema

    async def _arun(
        self,
        channel_id: int,
        content: str | None = None,
        tts: bool = False,
        embeds: list[dict] | None = None,
        files: list[str] | None = None,
        reference: int | None = None,
    ) -> str:
        try:
            channel = await self.client.fetch_channel(channel_id)
            if not channel:
                raise ToolException(f"Channel {channel_id} not found")

            # Convert file paths to File objects
            file_objects = [File(fp) for fp in (files or [])]

            # Convert embed dicts to Embed objects
            embed_objects = [Embed.from_dict(e) for e in (embeds or [])]

            # Create message reference if needed
            msg_reference = None
            if reference:
                msg_reference = MessageReference(
                    message_id=reference,
                    channel_id=channel_id,
                    fail_if_not_exists=False,
                )

            # Send the message with all options
            message = await channel.send(
                content=content,
                tts=tts,
                embeds=embed_objects,
                files=file_objects,
                reference=msg_reference,
            )
            return f"Message sent successfully with ID: {message.id}"
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to send message: {str(e)}") from e
