from typing import Any

from langchain_core.tools.base import BaseTool, BaseToolkit

from ...tools.discord.add_reaction import DiscordAddReactionTool
from ...tools.discord.list_emojis import DiscordListEmojisTool
from ...tools.discord.list_messages import DiscordListMessagesTool
from ...tools.discord.reply_message import DiscordReplyMessageTool
from ...tools.discord.send_message import DiscordSendMessageTool


class DiscordToolkit(BaseToolkit):
    """Toolkit for Discord operations."""

    client: Any = None  #: :meta private:

    def get_tools(self) -> list[BaseTool]:
        """Get the tools in the toolkit.

        Returns:
            List of Discord tools.
        """
        return [
            DiscordAddReactionTool(client=self.client),
            DiscordListEmojisTool(client=self.client),
            DiscordListMessagesTool(client=self.client),
            DiscordReplyMessageTool(client=self.client),
            DiscordSendMessageTool(client=self.client),
        ]
