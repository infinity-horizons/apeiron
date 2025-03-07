from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import ToolException
from discord.errors import Forbidden, NotFound


@tool
async def list_messages(
    *,
    limit: int = 100,
    channel_id: int | None = None,
    before: str | None = None,
    after: str | None = None,
    run_config: RunnableConfig,
) -> list[dict]:
    """Read messages from a Discord channel with optional filters.

    Args:
        limit: Number of messages to retrieve (max 100)
        channel_id: Optional ID of the channel to read messages from
        before: Optional message ID to read messages before
        after: Optional message ID to read messages after
        run_config: Runtime configuration containing message and client context

    Returns:
        list[dict]: List of message objects containing id, content, author, timestamp, and reference
    """
    try:
        if channel_id is None:
            message = run_config.get("message")
            if not message:
                raise ToolException("No channel_id provided and no message in context")
            channel = message.channel
        else:
            client = run_config.get("client")
            if not client:
                raise ToolException("No Discord client in context")
            channel = await client.fetch_channel(channel_id)

        kwargs = {"limit": min(limit, 100)}
        if before:
            kwargs["before"] = before
        if after:
            kwargs["after"] = after

        messages = []
        async for message in channel.history(**kwargs):
            ref_id = None
            if message.reference:
                ref_id = str(message.reference.message_id)

            messages.append(
                {
                    "id": str(message.id),
                    "content": message.content,
                    "author": str(message.author),
                    "timestamp": str(message.created_at),
                    "reference": ref_id,
                }
            )
        return messages
    except (Forbidden, NotFound) as e:
        raise ToolException(f"Failed to read messages: {str(e)}") from e
