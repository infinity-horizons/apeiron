import logging
import os

import click
import discord
from langchain_core.globals import set_debug, set_verbose
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import trim_messages
from langgraph.pregel import Pregel

from .agents.roast import create_agent
from .chat_message_histories.discord import DiscordChatMessageHistory
from .chat_models.mistral import ChatMistralAI
from .toolkits.discord.toolkit import DiscordToolkit
from .tools.discord.utils import is_client_user

logger = logging.getLogger(__name__)


def create_bot(bot: discord.Bot, model: BaseChatModel, pregel: Pregel):
    """Create and configure the Discord client with all intents."""

    @bot.listen
    async def on_message(message: discord.Message):
        if is_client_user(bot, message):
            return

        if not bot.user.mentioned_in(message):
            logger.debug(f"Message not mentioning bot: {message.content}")
            return

        try:
            chat_history = DiscordChatMessageHistory(bot)
            await chat_history.load_messages(message.channel.id)

            messages = trim_messages(
                chat_history.messages,
                token_counter=model,
                strategy="last",
                max_tokens=2000,
                start_on="human",
                end_on=("human", "tool"),
                include_system=True,
            )

            async with message.channel.typing():
                result = await pregel.ainvoke(
                    {"messages": messages},
                    config={
                        "configurable": {"message": message},
                    },
                )
                await message.channel.send(result["messages"][-1].content)
        except Exception as e:
            logger.error(f"Error generating roast: {str(e)}")

    return bot


def init(debug: bool, verbose: bool):
    # Set debug and verbose modes if flags are enabled
    if debug:
        set_debug(True)
    if verbose:
        set_verbose(True)

    # Get log level from environment variable, default to INFO if not set
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    level_names = logging.getLevelNamesMapping()
    try:
        log_level = level_names[log_level_str.upper()]
    except KeyError as e:
        raise ValueError(f"Invalid log level: {log_level_str}") from e

    logging.basicConfig(level=log_level)


def get_agent_model(agent_provider: str, agent_model: str) -> BaseChatModel:
    """Initialize the agent model based on the provider and model name."""
    if agent_provider == "mistralai":
        return ChatMistralAI(model_name=agent_model)
    else:
        raise ValueError(f"Invalid agent provider: {agent_provider}")


def parse_feature_gates(feature_gates_str: str) -> dict[str, bool]:
    """Parse feature gates from a string into a dictionary."""
    feature_gates_dict = {}
    for feature_gate in feature_gates_str.split(","):
        feature_gate = feature_gate.strip()
        if feature_gate:
            feature_gates_dict[feature_gate] = True
    return feature_gates_dict


@click.command()
@click.option("--agent-provider", help="Agent provider", default="mistralai")
@click.option("--agent-model", help="Agent model", default="pixtral-12b-2409")
@click.option("--feature-gates", help="Enable feature gates", default="")
@click.option("--debug", is_flag=True, help="Enable debug logging", default=False)
@click.option("--verbose", is_flag=True, help="Enable verbose logging", default=False)
def main(
    agent_provider: str,
    agent_model: str,
    feature_gates: str,
    debug: bool,
    verbose: bool,
):
    """Run the Discord bot agent"""
    init(debug, verbose)

    # Parse feature gates
    feature_gates_dict = parse_feature_gates(feature_gates)

    # Initialize the MistralAI model
    model = get_agent_model(agent_provider, agent_model)

    # Initialize the Discord client
    discord_bot = discord.Bot(intents=discord.Intents.default())
    tools = []
    if feature_gates_dict.get("AgentDiscordToolkit", False):
        tools = DiscordToolkit(client=discord_bot).get_tools()
    graph = create_agent(tools=tools, model=model)
    bot = create_bot(bot=discord_bot, model=model, pregel=graph)

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is not set")

    bot.run(token)


if __name__ == "__main__":
    main()
