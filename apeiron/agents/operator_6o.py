import logging
from pathlib import Path
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from apeiron.agents.utils import load_prompt

logger = logging.getLogger(__name__)


def create_agent(**kwargs) -> BaseChatModel:
    """Create the Operator 6O agent for the graph.

    Args:
        tools: Sequence of tools available to the agent
        model: Base chat model to use
        **kwargs: Additional arguments passed to create_react_agent

    Returns:
        Configured chat model agent
    """
    return create_react_agent(
        name="Operator 6O",
        checkpointer=InMemorySaver(),
        prompt=load_prompt(
            Path(__file__).parent.resolve() / f"{Path(__file__).stem}.yaml",
        ),
        version="v2",
        **kwargs,
    )
