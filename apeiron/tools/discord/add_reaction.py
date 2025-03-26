from discord.errors import Forbidden, NotFound
from discord import Client
from langchain_core.runnables import RunnableConfig
from langchain_core.tools.base import ToolException
from langchain_core.tools import tool
from pydantic import BaseModel, Field


class AddReactionSchema(BaseModel):
    """Arguments for adding reactions to Discord messages."""

    emoji: str = Field(description="The emoji to react with")
    message_id: int | None = Field(
        None, description="ID of the message to add reaction to"
    )
    channel_id: int | None = Field(
        None, description="ID of the channel containing the message"
    )


def create_add_reaction_tool(client: Client):
    """Create a tool for adding reactions to Discord messages."""

    @tool(name="add_reaction", description="Add a reaction to a message in a Discord channel", args_schema=AddReactionSchema)
    async def add_reaction(
        emoji: str,
        message_id: int | None = None,
        channel_id: int | None = None,
        config: RunnableConfig | None = None,
    ) -> str:
        """Add a reaction to a message in a Discord channel.

        Args:
            emoji: The emoji to react with.
            message_id: ID of the message to add reaction to.
            channel_id: ID of the channel containing the message.
            config: Optional RunnableConfig object.

        Returns:
            Confirmation message.

        Raises:
            ToolException: If the reaction addition fails.
        """
        if message_id is None and config:
            message_id = config.get("configurable").get("message_id")
        if channel_id is None and config:
            channel_id = config.get("configurable").get("channel_id")
        try:
            channel = await client.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
            await message.add_reaction(emoji)
            return f"Reaction {emoji} added successfully to message {message_id}"
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to add reaction: {str(e)}") from e

    return add_reaction
