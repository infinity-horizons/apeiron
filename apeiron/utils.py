import logging
import os

import discord
import uvicorn
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


def get_logging_level() -> int:
    """Get the logging level from the environment variable.
    Returns:
        Logging level as an integer
    """
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    level_names = logging.getLevelNamesMapping()
    try:
        return level_names[log_level_str.upper()]
    except KeyError as e:
        raise ValueError(f"Invalid log level: {log_level_str}") from e


def create_logging_handlers():
    match os.getenv("LOG_FORMAT", "uvicorn"):
        case "uvicorn":
            handler = logging.StreamHandler()
            handler.setFormatter(
                uvicorn.logging.DefaultFormatter(
                    "{levelprefix} {message}", style="{", use_colors=True
                )
            )
            return [handler]
        case _:
            return []


def trim_messages_images(
    messages: list[BaseMessage], max_images: int = 8
) -> list[BaseMessage]:
    """Filter chat history to keep only a maximum number of images.

    Args:
        messages: List of messages to filter
        max_images: Maximum number of images to keep (default: 8)

    Returns:
        List of filtered messages with limited image attachments
    """
    image_count = 0
    slice_index = 0

    # Process messages in reverse order (newest to oldest)
    for i, message in enumerate(reversed(messages)):
        if isinstance(message.content, list):
            # Count images in the message content
            for content in message.content:
                if isinstance(content, dict) and content.get("type") == "image_url":
                    image_count += 1
                    if image_count > max_images:
                        slice_index = len(messages) - i - 1
                        break
        if image_count > max_images:
            break

    # Return messages from slice_index to the end
    return messages[slice_index + 1 :]


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
