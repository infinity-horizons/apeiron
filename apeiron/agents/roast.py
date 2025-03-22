import logging
from collections.abc import Sequence
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools.base import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore

from apeiron.agents.utils import load_prompt

logger = logging.getLogger(__name__)


def create_agent(tools: Sequence[BaseTool], model: BaseChatModel, **kwargs):
    """Create the roast generation node for the graph."""
    return create_react_agent(
        name="Roast",
        model=model,
        tools=tools,
        store=InMemoryStore(),
        checkpointer=InMemorySaver(),
        prompt=load_prompt(
            Path(__file__).parent.resolve() / f"{Path(__file__).stem}.yaml",
        ),
        version="v2",
        **kwargs,
    )
