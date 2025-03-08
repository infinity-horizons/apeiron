import logging
import os

import click
import discord
from discord import app_commands
from langchain_core.globals import set_debug, set_verbose
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import trim_messages
from langchain_mistralai.chat_models import ChatMistralAI
from langgraph.pregel import Pregel

from .agents.roast import create_agent
from .chat_message_histories.discord import DiscordChatMessageHistory
from .toolkits.discord.toolkit import DiscordToolkit
from .tools.discord.utils import is_client_user

logger = logging.getLogger(__name__)


def create_command_tree(client: discord.Client) -> app_commands.CommandTree:
    """Create and configure the command tree."""
    tree = app_commands.CommandTree(client)

    @tree.command(name="help", description="Shows help information about commands")
    async def help(interaction: discord.Interaction):
        help_embed = discord.Embed(
            title="Bot Help",
            description="List of available commands:",
            color=discord.Color.blue(),
        )
        help_embed.add_field(
            name="/help", value="Shows this help message", inline=False
        )
        await interaction.response.send_message(embed=help_embed)

    return tree


def create_bot(
    client: discord.Client, model: BaseChatModel, pregel: Pregel
) -> discord.Client:
    """Create and configure the Discord client with all intents."""
    tree = create_command_tree(client)

    @client.event
    async def setup_hook():
        await tree.sync()

    @client.event
    async def on_message(message: discord.Message):
        if is_client_user(client, message):
            return

        if not client.user.mentioned_in(message):
            logger.debug(f"Message not mentioning bot: {message.content}")
            return

        if message.channel.name not in ["commands", "roast"]:
            logger.debug(f"Message not in roast channel: {message.content}")
            return

        try:
            chat_history = DiscordChatMessageHistory(client)
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

    return client


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

    discord.utils.setup_logging(level=log_level)


@click.command()
@click.option("--debug", is_flag=True, help="Enable debug logging", default=False)
@click.option("--verbose", is_flag=True, help="Enable verbose logging", default=False)
def main(debug: bool, verbose: bool):
    """Run the Discord bot agent"""
    init(debug, verbose)

    # Initialize the MistralAI model
    model = ChatMistralAI(temperature=0.7, model_name="pixtral-12b-2409")

    # Initialize the Discord client
    discord_client = discord.Client(intents=discord.Intents.all())
    discord_toolkit = DiscordToolkit(client=discord_client)
    graph = create_agent(tools=discord_toolkit.get_tools(), model=model)
    bot = create_bot(client=discord_client, model=model, pregel=graph)

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is not set")

    bot.run(token)


if __name__ == "__main__":
    main()
