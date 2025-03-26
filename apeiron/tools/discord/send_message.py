from discord import Client, Embed, File, MessageReference
from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field


class SendMessageInput(BaseModel):
    """Arguments for sending Discord messages."""

    content: str | None = Field(None, description="The content of the message to send")
    channel_id: int | None = Field(
        None, description="ID of the channel to send the message to"
    )
    tts: bool = Field(False, description="Whether to send as text-to-speech message")
    embeds: list[dict] | None = Field(None, description="List of embed dictionaries")
    files: list[str] | None = Field(None, description="List of file paths to send")
    reference: int | None = Field(None, description="Message ID to reply to")
    stickers: list[int] | None = Field(None, description="List of sticker IDs to send")
    suppress_embeds: bool = Field(
        False, description="Whether to suppress embeds in this message"
    )
    allowed_mentions: dict | None = Field(
        None, description="Controls which mentions are allowed in the message"
    )
    components: list[dict] | None = Field(
        None, description="Message components (buttons, select menus, etc.)"
    )
    thread_name: str | None = Field(
        None, description="Creates a thread with this name from this message"
    )
    silent: bool = Field(
        False,
        description="Whether to send the message without triggering notifications",
    )


def create_send_message_tool(client: Client):
    """Create a tool for sending messages to a Discord channel."""

    @tool(args_schema=SendMessageInput)
    async def send_message(
        content: str | None = None,
        channel_id: int | None = None,
        tts: bool = False,
        embeds: list[dict] | None = None,
        files: list[str] | None = None,
        reference: int | None = None,
        stickers: list[int] | None = None,
        suppress_embeds: bool = False,
        allowed_mentions: dict | None = None,
        components: list[dict] | None = None,
        thread_name: str | None = None,
        silent: bool = False,
        config: RunnableConfig | None = None,
    ) -> str:
        """Send a message to a Discord channel.

        Args:
            content: The content of the message to send.
            channel_id: The ID of the channel to send the message to.
            tts: Whether to send as text-to-speech message.
            embeds: List of embed dictionaries.
            files: List of file paths to send.
            reference: Message ID to reply to.
            stickers: List of sticker IDs to send.
            suppress_embeds: Whether to suppress embeds in this message.
            allowed_mentions: Controls which mentions are allowed in the message.
            components: Message components (buttons, select menus, etc.).
            thread_name: Creates a thread with this name from this message.
            silent: Whether to send the message without triggering notifications.
            config: Optional runnable config object.

        Returns:
            The ID of the sent message.

        Raises:
            ToolException: If the message fails to send.
        """
        if not channel_id and config:
            channel_id = config.get("configurable").get("channel_id")
        try:
            channel = await client.fetch_channel(channel_id)
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
                stickers=stickers,
                suppress_embeds=suppress_embeds,
                allowed_mentions=allowed_mentions,
                components=components,
                silent=silent,
            )

            # Create thread if name is provided
            if thread_name and message:
                await message.create_thread(name=thread_name)
            return f"Message sent successfully with ID: {message.id}"
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to send message: {str(e)}") from e

    return send_message
