from discord.errors import Forbidden, NotFound
from langchain_core.runnables import RunnableConfig
from langchain_core.tools.base import ToolException
from pydantic import BaseModel, Field

from apeiron.tools.discord.base import BaseDiscordTool
from apeiron.tools.discord.get_message import to_dict


class ListMessagesSchema(BaseModel):
    """Arguments for listing Discord messages."""

    channel_id: int | None = Field(
        None, description="The ID of the channel to read messages from"
    )
    before: str | None = Field(
        None, description="Optional message ID to read messages before"
    )
    after: str | None = Field(
        None, description="Optional message ID to read messages after"
    )
    around: str | None = Field(
        None, description="Optional message ID to read messages around"
    )
    limit: int = Field(100, description="Number of messages to retrieve (max 100)")


class DiscordListMessagesTool(BaseDiscordTool):
    """Tool for reading messages from a Discord channel with optional filters."""

    name: str = "list_messages"
    description: str = "Read messages from a Discord channel with optional filters"
    args_schema: type[ListMessagesSchema] = ListMessagesSchema

    async def _arun(
        self,
        channel_id: int | None = None,
        before: str | None = None,
        after: str | None = None,
        around: str | None = None,
        limit: int = 100,
        config: RunnableConfig | None = None,
    ) -> list[dict]:
        """Read messages from a Discord channel with optional filters.

        Args:
            channel_id: ID of the channel to read messages from.
            before: Optional message ID to read messages before.
            after: Optional message ID to read messages after.
            limit: Number of messages to retrieve (max 100).
            config: Optional RunnableConfig object.

        Returns:
            List containing message objects with metadata and content.

        Raises:
            ToolException: If the messages fail to read.
        """
        if channel_id is None and config:
            channel_id = config.configurable.get("channel_id")
        try:
            channel = await self.client.fetch_channel(channel_id)
            kwargs = {"limit": limit}
            if before:
                kwargs["before"] = before
            if after:
                kwargs["after"] = after
            if around:
                kwargs["around"] = around

            messages = []
            async for message in channel.history(**kwargs):
                messages.append(to_dict(message))
            return messages
        except (Forbidden, NotFound) as e:
            raise ToolException(f"Failed to read messages: {str(e)}") from e
