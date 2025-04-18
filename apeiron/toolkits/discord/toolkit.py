from typing import Any

from langchain_core.tools.base import BaseTool, BaseToolkit

from apeiron.tools.discord.add_reaction import create_add_reaction_tool
from apeiron.tools.discord.get_channel import create_get_channel_tool
from apeiron.tools.discord.get_emoji import create_get_emoji_tool
from apeiron.tools.discord.get_guild import create_get_guild_tool
from apeiron.tools.discord.get_message import create_get_message_tool
from apeiron.tools.discord.get_user import create_get_user_tool
from apeiron.tools.discord.list_channels import create_list_channels_tool
from apeiron.tools.discord.list_emojis import create_list_emojis_tool
from apeiron.tools.discord.list_members import create_list_members_tool
from apeiron.tools.discord.list_messages import create_list_messages_tool
from apeiron.tools.discord.search_members import create_search_members_tool
from apeiron.tools.discord.send_message import create_send_message_tool


class DiscordToolkit(BaseToolkit):
    """Toolkit for Discord operations."""

    client: Any = None  #: :meta private:

    def get_tools(self) -> list[BaseTool]:
        """Get the tools in the toolkit.

        Returns:
            List of Discord tools.
        """
        return [
            create_add_reaction_tool(self.client),
            create_get_channel_tool(self.client),
            create_get_emoji_tool(self.client),
            create_get_guild_tool(self.client),
            create_get_message_tool(self.client),
            create_get_user_tool(self.client),
            create_list_channels_tool(self.client),
            create_list_emojis_tool(self.client),
            create_list_members_tool(self.client),
            create_list_messages_tool(self.client),
            create_search_members_tool(self.client),
            create_send_message_tool(self.client),
        ]
