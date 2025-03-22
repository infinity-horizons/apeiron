import logging
from collections.abc import Sequence
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools.base import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field

from apeiron.agents.utils import load_prompt

logger = logging.getLogger(__name__)


class Response(BaseModel):
    """Response format for Operator 6O."""

    status: str = Field(..., description="Status of the response: 'success' or 'error'")
    reason: str | None = Field(None, description="Reason for error if status is 'error'")


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
