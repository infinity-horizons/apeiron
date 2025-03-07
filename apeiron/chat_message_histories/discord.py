from discord import Attachment, Client, Message
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class DiscordChatMessageHistory(BaseChatMessageHistory):
    """Chat message history that stores Discord messages."""

    def __init__(self, discord_client: Client) -> None:
        """Initialize with Discord client."""
        self.discord_client = discord_client
        self.messages: list[BaseMessage] = []

    def add_message(self, message: Message) -> None:
        """Add a Discord message to the store."""
        self.messages.append(self._convert_message(message))

    def clear(self) -> None:
        """Clear messages from the store."""
        self.messages = []

    async def load_messages(self, channel_id: int, limit: int | None = None) -> None:
        """Load messages from a Discord channel into the history.

        Args:
            channel_id: ID of the channel to load messages from
            limit: Maximum number of messages to load (None for no limit)
        """
        channel = self.discord_client.get_channel(channel_id)
        if not channel:
            return

        self.clear()
        async for message in channel.history(limit=limit):
            self.add_message(message)

        # Reverse to maintain chronological order
        self.messages.reverse()

    def _convert_message(self, message: Message) -> BaseMessage:
        """Convert Discord message to LangChain message format."""
        if message.attachments:
            content = []
            text_content = _convert_text_content(message)
            if text_content:
                content.append(text_content)
            for att in message.attachments:
                image_content = _create_image_content(att)
                if image_content:
                    content.append(image_content)
        else:
            content = _normalize_text_content(message.content)
        return (
            AIMessage(content=content)
            if message.author == self.discord_client.user
            else HumanMessage(content=content)
        )


def _create_image_content(attachment) -> dict | None:
    """Create image content from Discord attachment."""
    if _is_supported_content_type(attachment):
        return {"type": "image_url", "image_url": attachment.url}
    return None


def _convert_text_content(message: Message) -> dict | None:
    """Create text content from Discord message."""
    if message.content:
        return {"type": "text", "text": _normalize_text_content(message.content)}
    return None

def _normalize_text_content(content: str) -> str:
    """Normalize text content by ensuring it's not empty."""
    return content if content else " "

SUPPORTED_CONTENT_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]


def _is_supported_content_type(attachment: Attachment) -> bool:
    """Check if attachment has a supported content type and extension."""
    return (
        attachment.content_type
        and attachment.content_type in SUPPORTED_CONTENT_TYPES
    )
