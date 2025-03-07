from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_core.tools.base import ToolException
from discord.errors import Forbidden, NotFound


@tool
async def list_emojis(
    guild_id: int | None = None,
    *,
    run_config: RunnableConfig,
) -> list[dict]:
    """List all emojis in a Discord guild.

    Args:
        guild_id: Optional ID of the guild to list emojis from
        run_config: Runtime configuration containing message and client context

    Returns:
        list[dict]: List of emoji objects containing id, name, animated status, and URL
    """
    try:
        if guild_id is None:
            message = run_config.get("message")
            if not message:
                raise ToolException("No guild_id provided and no message in context")
            guild = message.guild
        else:
            client = run_config.get("client")
            if not client:
                raise ToolException("No Discord client in context")
            guild = await client.fetch_guild(guild_id)

        emojis = await guild.fetch_emojis()

        return [
            {
                "id": emoji.id,
                "name": emoji.name,
                "animated": emoji.animated,
                "url": str(emoji.url),
            }
            for emoji in emojis
        ]
    except (Forbidden, NotFound) as e:
        raise ToolException(f"Failed to list emojis: {str(e)}") from e
