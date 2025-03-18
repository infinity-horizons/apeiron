from enum import Enum

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Enum for different types of Discord message actions."""

    SEND = "send"
    REPLY = "reply"
    NOOP = "noop"


class MessageContent(BaseModel):
    """Model for message content with optional reference."""

    content: str = Field(..., description="The text content of the message")
    reference_message_id: str | None = Field(
        None,
        description="The ID of the message to reply to (only used with REPLY action)",
    )


class DiscordAction(BaseModel):
    """Model for Discord message actions with validation."""

    action_type: ActionType = Field(..., description="The type of action to take")
    message: MessageContent | None = Field(
        None,
        description=(
            "Message content and reference (required for SEND and REPLY actions)"
        ),
    )

    def model_post_init(self, *args, **kwargs) -> None:
        """Validate that message is provided when required."""
        if self.action_type in (ActionType.SEND, ActionType.REPLY) and not self.message:
            raise ValueError(
                f"Message content is required for action type {self.action_type}"
            )
        if (
            self.action_type == ActionType.REPLY
            and not self.message.reference_message_id
        ):
            raise ValueError("Reference message ID is required for REPLY action")
