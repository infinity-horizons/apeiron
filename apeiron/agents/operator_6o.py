import logging
from collections.abc import Sequence
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.tools.base import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore

from apeiron.agents.utils import load_messages

logger = logging.getLogger(__name__)


def create_agent(tools: Sequence[BaseTool], model: BaseChatModel, **kwargs):
    """Create the Operator 6O agent for the graph."""
    return create_react_agent(
        name="Operator 6O",
        model=model,
        tools=tools,
        store=InMemoryStore(),
        checkpointer=InMemorySaver(),
        version="v2",
        **kwargs,
    )


def get_messages() -> list[HumanMessage | AIMessage | SystemMessage]:
    """Get the messages for the Operator 6O agent."""
    return load_messages(
        Path(__file__).parent.resolve() / f"{Path(__file__).stem}.yaml",
    )
