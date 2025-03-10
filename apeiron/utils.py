import logging
from functools import reduce

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
    img_count = 0
    slice_index = len(messages)

    for i, message in enumerate(messages):
        if isinstance(message.content, str):
            continue

        for item in message.content:
            if item.get("type") == "image_url":
                img_count += 1
                if img_count > max_images:
                    slice_index = i
                    break
        if img_count > max_images:
            break

    return messages[:slice_index]


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
