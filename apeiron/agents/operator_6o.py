import logging
from collections.abc import Sequence
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools.base import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field

from apeiron.agents.utils import load_prompt

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Type of action to take."""

    SEND = "send"
    REPLY = "reply"


class SendResponse(BaseModel):
    """Response format for sending new messages."""

    type: Literal["send"] = "send"
    content: str = Field(
        description="Content of the message to send",
    )


class ReplyResponse(BaseModel):
    """Response format for reply messages."""

    type: Literal["reply"] = "reply"
    content: str = Field(
        description="Content of the reply message",
    )
    message_id: int = Field(
        description="ID of the message to reply to",
    )


class NoopResponse(BaseModel):
    """Response format for no operation needed."""

    type: Literal["noop"] = "noop"


Response = Annotated[
    SendResponse | ReplyResponse | NoopResponse, Field(discriminator="type")
]


def create_agent(tools: Sequence[BaseTool], model: BaseChatModel, **kwargs):
    """Create the Operator 6O agent for the graph."""
    return create_react_agent(
        name="Operator 6O",
        model=model,
        tools=tools,
        store=InMemoryStore(),
        checkpointer=InMemorySaver(),
        prompt=load_prompt(
            Path(__file__).parent.resolve() / f"{Path(__file__).stem}.yaml",
        ),
        response_format=Response,
        version="v2",
        **kwargs,
    )
