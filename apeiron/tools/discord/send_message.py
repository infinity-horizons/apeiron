from typing import TYPE_CHECKING

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import ToolException

if TYPE_CHECKING:
    # This is for linting and IDE typehints
    from discord.errors import Forbidden, NotFound


@tool
async def send_message(
    content: str,
    channel_id: int | None = None,
    *,
    run_config: RunnableConfig,
) -> str:
    """Send a message to a Discord channel.

    Args:
        content: The content of the message to send
        channel_id: Optional ID of the channel to send the message to
        run_config: Runtime configuration containing message and client context

    Returns:
        str: Confirmation message with the sent message ID
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

        message = await channel.send(content)

        return f"Message sent successfully with ID: {message.id}"
    except (Forbidden, NotFound) as e:
        raise ToolException(f"Failed to send message: {str(e)}") from e
