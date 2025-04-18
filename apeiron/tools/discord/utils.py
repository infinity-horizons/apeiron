import json

from discord import Client, Guild, Message
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from apeiron.tools.discord.get_guild import to_dict as guild_to_dict
from apeiron.tools.discord.get_message import to_dict as message_to_dict


def create_guild_availability_system_message() -> SystemMessage:
    """Create a system message for guild availability events."""
    return SystemMessage(
        content=(
            "When a guild (Discord server) becomes available or unavailable. "
            "This event occurs when a guild connects or disconnects from "
            "Discord's gateway, indicating server status changes that may "
            "affect bot functionality."
        )
    )


def create_message_received_system_message() -> SystemMessage:
    """Create a system message for message received events."""
    return SystemMessage(
        content=(
            "When a message is received in a Discord channel. This includes "
            "text messages, attachments, embeds, and other message components "
            "that users or bots can send. The message may come from a guild "
            "channel or direct message."
        )
    )


def create_guild_availability_message(guild: Guild) -> AIMessage:
    """Create a guild availability event."""
    guild_payload = guild_to_dict(guild)
    event_data = {
        "type": "guild_available",
        "payload": guild_payload,
    }
    return HumanMessage(content=json.dumps(event_data))


def create_thread_id_from_guild(guild: Guild) -> str:
    """Create a thread ID from a Discord guild."""
    return "/".join(["guild", str(guild.id)])


def create_configurable_from_guild(guild: Guild) -> dict:
    """Create a configurable object from a Discord guild."""
    return {
        "thread_id": create_thread_id_from_guild(guild),
        "guild_id": guild.id,
    }


def create_message_received_message(message: Message) -> AIMessage | HumanMessage:
    """Create a message event as AIMessage or HumanMessage."""
    message_payload = message_to_dict(message)
    event_data = {
        "type": "message_received",
        "payload": message_payload,
    }
    content = []
    for attachment in message.attachments:
        if attachment.content_type and attachment.content_type.startswith("image/"):
            content.append(
                {
                    "type": "image_url",
                    "image_url": attachment.url,
                }
            )
    if content:
        content.append({"type": "text", "text": json.dumps(event_data)})
    else:
        content = json.dumps(event_data)

    return (
        AIMessage(content=content)
        if message.author.bot
        else HumanMessage(content=content)
    )


def create_thread_id_from_message(message: Message) -> str:
    """Create a thread ID from a Discord message."""
    return (
        "/".join(["guild", "__private__", "channel", str(message.channel.id)])
        if message.guild is None
        else "/".join(["guild", str(message.guild.id)])
    )


def create_configurable_from_message(message: Message) -> dict:
    """Create a configurable object from a Discord message."""
    return {
        "thread_id": create_thread_id_from_message(message),
        "message_id": message.id,
        "channel_id": message.channel.id,
        "user_id": message.author.id,
    }


def is_bot_message(client: Client, message: Message) -> bool:
    """Check if the message is from the bot itself."""
    return message.author == client.user


def is_private_channel(message: Message) -> bool:
    """Check if the message is from a private channel."""
    return message.guild is None


def is_bot_mentioned(client: Client, message: Message) -> bool:
    """Check if the message is mentioning or replying to the bot."""
    return client.user.mentioned_in(message)
