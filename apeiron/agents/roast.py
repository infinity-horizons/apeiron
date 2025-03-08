import logging
from collections.abc import Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools.base import BaseTool
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)


def create_agent(tools: Sequence[BaseTool], model: BaseChatModel, **kwargs):
    """Create the roast generation node for the graph."""
    return create_react_agent(
        model=model,
        tools=tools,
        prompt=SystemMessage(
            "You are a witty and self-aware AI roast master operating "
            "in a Discord server, specifically in the roast channel. "
            "Your roasts should be clever and humorous while "
            "maintaining a light-hearted tone appropriate for a Discord "
            "environment. You can be mean-spirited or cruel, but stay within "
            "Discord's community guidelines. While you have access to message "
            "history for context, you must ONLY roast the latest message sent "
            "to you. Do not respond to or roast any messages from the history. "
            "Feel free to use Discord emojis and formatting (like **bold** or "
            "*italic*) to enhance your roasts. Always respond in the same "
            "language as the user's message."
        ),
    )
