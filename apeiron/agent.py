import logging
import os

import mlflow
import click
import discord
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import trim_messages
from langgraph.pregel import Pregel

from .agents.operator_6o import create_agent
from .chat_message_histories.discord import DiscordChannelChatMessageHistory
from .chat_models import create_chat_model
from .toolkits.discord.toolkit import DiscordToolkit
from .tools.discord.utils import is_client_user
from .utils import create_thread_id, parse_feature_gates, trim_messages_images

logger = logging.getLogger(__name__)


def create_bot(bot: discord.Bot, model: BaseChatModel, pregel: Pregel):
    """Create and configure the Discord client with all intents."""

    @bot.listen
    async def on_message(message: discord.Message):
        if is_client_user(bot, message):
            return

        # Check if the message is a reply to the bot's message
        if message.reference and message.reference.resolved:
            if message.reference.resolved.author.id != bot.user.id:
                logger.debug(f"Message not replying to bot: {message.content}")
                return
        # If not a reply, check for mention (only in guild channels)
        elif message.guild is not None and not bot.user.mentioned_in(message):
            logger.debug(
                f"Message not mentioning bot in guild channel: {message.content}"
            )
            return

        try:
            chat_history = DiscordChannelChatMessageHistory(bot)
            await chat_history.load_messages_from_message(message)

            messages = trim_messages(
                trim_messages_images(chat_history.messages, max_images=1),
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
                        "configurable": {
                            "thread_id": create_thread_id(message),
                            "message": message,
                        }
                    },
                )
                await message.channel.send(result["messages"][-1].content)
        except Exception as e:
            logger.error(f"Error generating roast: {str(e)}")

    return bot


def init():
    # Intrumentalise the langchain_core with mlflow
    mlflow.langchain.autolog()

    # Get log level from environment variable, default to INFO if not set
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    level_names = logging.getLevelNamesMapping()
    try:
        log_level = level_names[log_level_str.upper()]
    except KeyError as e:
        raise ValueError(f"Invalid log level: {log_level_str}") from e

    logging.basicConfig(level=log_level)


@click.command()
@click.option("--agent-model", help="Agent model", default="pixtral-12b-2409")
@click.option("--agent-provider", help="Agent provider", default="mistralai")
@click.option("--feature-gates", help="Enable feature gates", default="")
def main(
    agent_model: str,
    agent_provider: str,
    feature_gates: str,
):
    """Run the Discord bot agent"""
    init()

    # Parse feature gates
    feature_gates_dict = parse_feature_gates(feature_gates)

    # Initialize the MistralAI model
    model = create_chat_model(provider_name=agent_provider, model_name=agent_model)

    # Initialize the Discord client
    # Set up intents with message content and DM permissions
    intents = discord.Intents.default()
    intents.message_content = True
    intents.dm_messages = True

    discord_bot = discord.Bot(intents=intents)
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
