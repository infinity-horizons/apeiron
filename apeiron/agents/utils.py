from os import PathLike

import yaml
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder,
)


def _validate_message(message: dict) -> bool:
    """Validate if message has required fields."""
    return isinstance(message, dict) and "role" in message and "content" in message


def _create_message(
    role: str, content: str
) -> HumanMessage | AIMessage | SystemMessage | None:
    """Create appropriate message type based on role."""
    if not content:
        return None

    if role == "system":
        return SystemMessage(content=content)
    elif role == "human":
        return HumanMessage(content=content)
    elif role == "ai":
        return AIMessage(content=content)
    else:
        raise ValueError(f"Invalid role: {role}")


def _create_messages(
    messages: list[dict],
) -> list[HumanMessage | AIMessage | SystemMessage]:
    """Process a list of messages and convert them to appropriate message objects."""
    processed_messages = []
    for message in messages:
        if not _validate_message(message):
            raise ValueError("Invalid message format")

        msg = _create_message(message.get("role"), message.get("content"))
        if msg:
            processed_messages.append(msg)
    return processed_messages


def load_prompt(path: PathLike) -> ChatPromptTemplate:
    """Create the prompt template from the given YAML file."""
    with open(path) as f:
        prompt_config = yaml.safe_load(f)
    if not prompt_config:
        raise ValueError("Empty prompt configuration file")
    messages = (
        _create_messages(prompt_config["messages"])
        if "messages" in prompt_config
        else []
    )
    example_prompt = (
        _create_messages(prompt_config["example_messages"])
        if "example_messages" in prompt_config
        else []
    )
    examples = prompt_config.get("examples", [])
    if example_prompt and examples:
        messages.append(
            FewShotChatMessagePromptTemplate(
                example_prompt=example_prompt,
                examples=examples,
            )
        )
    messages.append(MessagesPlaceholder(variable_name="messages"))
    return ChatPromptTemplate.from_messages(messages)
