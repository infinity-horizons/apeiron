import logging
import os

import click
import discord
from discord import app_commands
from langchain_mistralai.chat_models import ChatMistralAI
from langgraph.graph import Graph
from langgraph.prebuilt import create_react_agent
from langchain_core.globals import set_debug, set_verbose

from .tools.discord.list_emojis import list_emojis
from .tools.discord.list_messages import list_messages
from .tools.discord.reply_message import reply_message
from .tools.discord.send_message import send_message
from .tools.discord.utils import from_discord_message, is_client_user

logger = logging.getLogger(__name__)


def create_roast_agent_graph(**kwargs):
    """Create the roast generation node for the graph."""
    return create_react_agent(
        model=ChatMistralAI(temperature=0.7, model_name="mistral-large-2411", **kwargs),
        tools=[
            list_emojis,
            list_messages,
            reply_message,
            send_message,
        ],
    )


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


def create_client(graph: Graph) -> discord.Client:
    """Create and configure the Discord client with all intents."""
    client = discord.Client(intents=discord.Intents.all())
    tree = create_command_tree(client)

    @client.event
    async def setup_hook():
        await tree.sync()

    @client.event
    async def on_message(message: discord.Message):
        if is_client_user(client, message):
            return

        if message.channel.name not in ["commands", "roast"]:
            return

        try:
            history_messages = []
            async for history_message in message.channel.history():
                if history_message.content == "":
                    continue
                history_messages.append(from_discord_message(client, history_message))
            history_messages.append(
                {
                    "role": "system",
                    "content": (
                        "You are Operator 6O, a witty and self-aware AI roast master operating "
                        f"in the {message.guild.name} Discord server, specifically in the "
                        f"#{message.channel.name} channel. You know you're an AI and embrace it in "
                        "your roasts. Your roasts should be clever and humorous while "
                        "maintaining a light-hearted tone appropriate for a Discord "
                        "environment. You can be mean-spirited or cruel, but stay within "
                        "Discord's community guidelines. While you have access to message "
                        "history for context, you must ONLY roast the latest message sent "
                        "to you. Do not respond to or roast any messages from the history. "
                        "Feel free to use Discord emojis and formatting (like **bold** or "
                        "*italic*) to enhance your roasts. Always respond in the same "
                        "language as the user's message."
                    ),
                }
            )
            history_messages.reverse()

            async with message.channel.typing():
                result = await graph.ainvoke(
                    {"messages": history_messages},
                    config={
                        "configurable": {
                            "thread_id": message.channel.id,
                            "client": client,
                            "message": message,
                        },
                    },
                )
                await message.channel.send(result["messages"][-1].content)
        except Exception as e:
            logger.error(f"Error generating roast: {str(e)}")

    return client

@click.command()
@click.option(
    "--debug", is_flag=True, help="Enable debug logging", default=False
)
@click.option(
    "--verbose", is_flag=True, help="Enable verbose logging", default=False
)
def main(debug: bool, verbose: bool):
    """Run the Discord bot agent"""
    # Set debug and verbose modes if flags are enabled
    if debug:
        set_debug(True)
    if verbose:
        set_verbose(True)

    # Initialize the Discord client
    graph = create_roast_agent_graph()
    client = create_client(graph)

    # Get log level from environment variable, default to INFO if not set
    log_level_str = os.getenv("LOG_LEVEL", "INFO")
    level_names = logging.getLevelNamesMapping()
    try:
        log_level = level_names[log_level_str.upper()]
    except KeyError as e:
        raise ValueError(f"Invalid log level: {log_level_str}") from e

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable is not set")

    logging.basicConfig(level=log_level)
    client.run(token, log_level=log_level)


if __name__ == "__main__":
    main()
