from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import ToolException
from discord.errors import Forbidden, NotFound


@tool
async def reply_message(
    content: str,
    message_id: int | None = None,
    channel_id: int | None = None,
    *,
    run_config: RunnableConfig,
) -> str:
    """Reply to a message in a Discord channel.

    Args:
        content: The content of the reply message
        message_id: Optional ID of the message to reply to
        channel_id: Optional ID of the channel containing the message
        run_config: Runtime configuration containing message and client context

    Returns:
        str: Confirmation message with the reply ID
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

        if message_id is None:
            message = run_config.get("message")
            if not message:
                raise ToolException("No message_id provided and no message in context")
        else:
            message = await channel.fetch_message(message_id)

        message = await message.reply(content)

        return f"Reply sent successfully with ID: {message.id}"
    except (Forbidden, NotFound) as e:
        raise ToolException(f"Failed to send reply: {str(e)}") from e
