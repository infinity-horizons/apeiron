from typing import Any

from langchain_core.tools.base import BaseTool, BaseToolkit

from apeiron.tools.discord.add_reaction import DiscordAddReactionTool
from apeiron.tools.discord.get_channel import DiscordGetChannelTool
from apeiron.tools.discord.get_emoji import DiscordGetEmojiTool
from apeiron.tools.discord.get_guild import DiscordGetGuildTool
from apeiron.tools.discord.get_message import DiscordGetMessageTool
from apeiron.tools.discord.get_user import DiscordGetUserTool
from apeiron.tools.discord.list_channels import DiscordListChannelsTool
from apeiron.tools.discord.list_emojis import DiscordListEmojisTool
from apeiron.tools.discord.list_members import DiscordListMembersTool
from apeiron.tools.discord.list_messages import DiscordListMessagesTool
from apeiron.tools.discord.search_members import DiscordSearchMembersTool
from apeiron.tools.discord.send_message import DiscordSendMessageTool


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
            DiscordGetChannelTool(client=self.client),
            DiscordGetEmojiTool(client=self.client),
            DiscordGetGuildTool(client=self.client),
            DiscordGetMessageTool(client=self.client),
            DiscordGetUserTool(client=self.client),
            DiscordListChannelsTool(client=self.client),
            DiscordListEmojisTool(client=self.client),
            DiscordListMembersTool(client=self.client),
            DiscordListMessagesTool(client=self.client),
            DiscordSearchMembersTool(client=self.client),
            DiscordSendMessageTool(client=self.client),
        ]
