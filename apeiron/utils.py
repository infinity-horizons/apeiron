import logging

from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


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
