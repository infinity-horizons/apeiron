from typing import TYPE_CHECKING

from discord import Client, Message
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.messages import BaseMessage


def is_client_user(client: Client, message: Message) -> bool:
    """Check if the message is from the bot user.
    Args:
        message: Discord Message object to check
    Returns:
        True if the message is from the bot user, False otherwise
    """
    return message.author == client.user


def from_discord_message(client: Client, message: Message) -> BaseMessage:
    """Convert Discord message to LangChain message format.

    Args:
        message: Discord Message object to convert

    Returns:
        LangChain BaseMessage (either HumanMessage or AIMessage)
    """
    # Determine if message is from the bot or a human user
    if is_client_user(client, message):
        return {"role": "assistant", "content": message.content}
    else:
        return {"role": "human", "content": message.content}
