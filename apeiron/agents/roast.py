import logging
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from apeiron.agents.utils import load_prompt

logger = logging.getLogger(__name__)


def create_agent(**kwargs):
    """Create the roast generation node for the graph."""
    return create_react_agent(
        name="Roast",
        checkpointer=InMemorySaver(),
        prompt=load_prompt(
            Path(__file__).parent.resolve() / f"{Path(__file__).stem}.yaml",
        ),
        version="v2",
        **kwargs,
    )
