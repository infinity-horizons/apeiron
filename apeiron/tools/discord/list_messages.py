from discord.errors import Forbidden, NotFound
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool
from apeiron.tools.discord.get_message import to_dict


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
    """Tool for reading messages from a Discord channel with optional filters."""

    name: str = "list_messages"
    description: str = "Read messages from a Discord channel with optional filters"
    args_schema: type[ListMessagesSchema] = ListMessagesSchema

    async def _arun(
        self,
        channel_id: int,
        before: str | None = None,
        after: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Read messages from a Discord channel with optional filters.

        Args:
            channel_id: ID of the channel to read messages from.
            before: Optional message ID to read messages before.
            after: Optional message ID to read messages after.
            limit: Number of messages to retrieve (max 100).

        Returns:
            List containing message objects with metadata and content.

        Raises:
            ToolException: If the messages fail to read.
        """
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
