from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool


class AddReactionSchema(BaseModel):
    """Arguments for adding reactions to Discord messages."""

    emoji: str = Field(description="The emoji to react with")
    message_id: int = Field(description="ID of the message to add reaction to")
    channel_id: int = Field(description="ID of the channel containing the message")


class DiscordAddReactionTool(BaseDiscordTool):
    """Tool for adding reactions to messages in a Discord channel."""

    name: str = "add_reaction"
    description: str = "Add a reaction to a message in a Discord channel"
    args_schema: type[AddReactionSchema] = AddReactionSchema

    async def _arun(
        self,
        emoji: str,
        message_id: int,
        channel_id: int,
    ) -> str:
        """Add a reaction to a message in a Discord channel.

        Args:
            emoji: The emoji to react with.
            message_id: ID of the message to add reaction to.
            channel_id: ID of the channel containing the message.

        Returns:
            Confirmation message.

        Raises:
            ToolException: If the reaction addition fails.
        """
        try:
            channel = await self.client.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            await message.add_reaction(emoji)
            return f"Reaction {emoji} added successfully to message {message_id}"
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to add reaction: {str(e)}") from e
