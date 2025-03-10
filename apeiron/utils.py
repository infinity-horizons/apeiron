from functools import reduce
import logging

import discord
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


def trim_messages_images(
    messages: list[BaseMessage], max_images: int = 8
) -> list[BaseMessage]:
    """Filter chat history to keep only a maximum number of images while
    preserving text content.

    Args:
        messages: List of messages to filter
        max_images: Maximum number of images to keep (default: 8)

    Returns:
        List of filtered messages with limited image attachments
    """

    def process_content_item(acc: tuple[list, int], item: dict) -> tuple[list, int]:
        content, img_count = acc
        if item.get("type") == "text":
            return (content + [item], img_count)
        elif item.get("type") == "image_url" and img_count < max_images:
            return (content + [item], img_count + 1)
        return (content, img_count)

    def process_message(
        acc: tuple[list, int], message: BaseMessage
    ) -> tuple[list, int]:
        filtered_messages, img_count = acc

        if isinstance(message.content, str):
            return (filtered_messages + [message.content], img_count)

        filtered_message, new_img_count = reduce(
            process_content_item, message.content, ([], img_count)
        )

        match filtered_message:
            case [{"type": "text", "content": content}]:
                return (
                    filtered_messages + [content],
                    new_img_count,
                )
            case _:
                return (filtered_messages + [message], new_img_count)

    # Process messages in reverse order and reduce
    filtered_messages, img_count = reduce(process_message, reversed(messages), ([], 0))

    logger.debug(f"Found {img_count} images in chat history")

    # Restore original chronological order
    return list(reversed(filtered_messages))


def parse_feature_gates(feature_gates_str: str) -> dict[str, bool]:
    """Parse feature gates from a string into a dictionary."""
    feature_gates_dict = {}
    for feature_gate in feature_gates_str.split(","):
        feature_gate = feature_gate.strip()
        if feature_gate:
            feature_gates_dict[feature_gate] = True
    return feature_gates_dict


def create_thread_id(message: discord.Message):
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
