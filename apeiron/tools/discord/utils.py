from discord import Client, Message
from langchain_core.messages import AIMessage, HumanMessage

from apeiron.tools.discord.get_message import to_dict


def format_message(payload: dict) -> str:
    """Format Discord message payload as markdown."""
    markdown_content = []

    # Message header
    markdown_content.append(f"## Discord Message")
    markdown_content.append(f"**ID:** `{payload['id']}`")
    markdown_content.append(f"**Channel:** `{payload['channel_id']}`")
    if payload.get('guild_id'):
        markdown_content.append(f"**Guild:** `{payload['guild_id']}`")
    markdown_content.append(f"**Timestamp:** {payload['timestamp']}")
    if payload.get('edited_timestamp'):
        markdown_content.append(f"**Edited:** {payload['edited_timestamp']}")

    # Author info
    author = payload['author']
    markdown_content.append(f"\n### Author")
    markdown_content.append(f"**Name:** {author['name']}")
    if author['display_name'] != author['name']:
        markdown_content.append(f"**Display Name:** {author['display_name']}")
    markdown_content.append(f"**ID:** `{author['id']}`")
    markdown_content.append(f"**Bot:** {'Yes' if author['bot'] else 'No'}")
    if author.get('avatar_url'):
        markdown_content.append(f"**Avatar:** [View Avatar]({author['avatar_url']})")

    # Message content
    if payload['content']:
        markdown_content.append(f"\n### Content")
        markdown_content.append(f"```\n{payload['content']}\n```")

    # Attachments
    if payload['attachments']:
        markdown_content.append(f"\n### Attachments ({len(payload['attachments'])})")
        for i, attachment in enumerate(payload['attachments'], 1):
            markdown_content.append(f"\n**Attachment {i}:**")
            markdown_content.append(f"- **Filename:** {attachment['filename']}")
            markdown_content.append(f"- **Size:** {attachment['size']} bytes")
            markdown_content.append(f"- **Type:** {attachment.get('content_type', 'Unknown')}")
            markdown_content.append(f"- **URL:** [Download]({attachment['url']})")
            if attachment.get('type') == 'image' and attachment.get('dimensions'):
                dims = attachment['dimensions']
                markdown_content.append(f"- **Dimensions:** {dims['width']}x{dims['height']}")

    # Referenced message
    if payload.get('reference'):
        ref = payload['reference']
        markdown_content.append(f"\n### Reply To")
        markdown_content.append(f"**Message ID:** `{ref['id']}`")
        markdown_content.append(f"**Author:** {ref['author']}")
        markdown_content.append(f"**Timestamp:** {ref['timestamp']}")
        if ref['content']:
            markdown_content.append(f"**Content:** {ref['content'][:100]}{'...' if len(ref['content']) > 100 else ''}")

    return "\n".join(markdown_content)


def create_chat_message(message: Message) -> AIMessage | HumanMessage:
    """Create a message event as AIMessage or HumanMessage."""
    text = format_message(to_dict(message))

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
        content.append({"type": "text", "text": text})
    else:
        content = text

    return (
        AIMessage(content=content)
        if message.author.bot
        else HumanMessage(content=content)
    )


def create_thread_id(message: Message) -> str:
    """Create a thread ID from a Discord message."""
    if message.guild is None:
        return "/".join(
            [
                "guild",
                "__private__",
                "channel",
                str(message.author.id),
            ]
        )
    if message.thread is None:
        return "/".join(
            [
                "guild",
                str(message.guild.id),
                "channel",
                str(message.channel.id),
            ]
        )
    return "/".join(
        [
            "guild",
            str(message.guild.id),
            "channel",
            str(message.channel.id),
            "thread",
            str(message.thread.id),
        ]
    )


def create_configurable(message: Message) -> dict:
    """Create a configurable object from a Discord message."""
    return {
        "thread_id": create_thread_id(message),
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
