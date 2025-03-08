import logging
from collections.abc import Sequence
from pathlib import Path

import yaml
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.tools.base import BaseTool
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)


def create_agent(tools: Sequence[BaseTool], model: BaseChatModel, **kwargs):
    """Create the Operator 6O agent for the graph."""
    return create_react_agent(
        model=model,
        tools=tools,
        prompt=_load_prompt(),
    )


def _load_prompt():
    """Create the Operator 6O prompt."""
    prompt_path = Path(__file__).parent.resolve() / "operator_6o.yaml"
    with prompt_path.open() as f:
        prompt_config = yaml.safe_load(f)
    messages = []
    for message in prompt_config["messages"]:
        if message["role"] == "system":
            messages.append(SystemMessage(content=message["content"]))
        elif message["role"] == "human":
            messages.append(HumanMessage(content=message["content"]))
        elif message["role"] == "ai":
            messages.append(AIMessage(content=message["content"]))
        else:
            raise ValueError(f"Invalid role: {message['role']}")
    example_prompt = []
    for message in prompt_config["example_messages"]:
        if message["role"] == "system":
            example_prompt.append(SystemMessage(content=message["content"]))
        elif message["role"] == "human":
            example_prompt.append(HumanMessage(content=message["content"]))
        elif message["role"] == "ai":
            example_prompt.append(AIMessage(content=message["content"]))
        else:
            raise ValueError(f"Invalid role: {message['role']}")
    return ChatPromptTemplate.from_messages(
        messages
        + [
            FewShotChatMessagePromptTemplate(
                example_prompt=example_prompt,
                examples=prompt_config["examples"],
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
