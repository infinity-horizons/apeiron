import logging
import os
from typing import TypedDict

import click
import discord
from discord import app_commands
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from langgraph.graph import END, START, Graph

logger = logging.getLogger(__name__)


class RoastState(TypedDict):
    server_name: str
    channel_name: str
    history: str
    message: str
    response: str | None


def create_roast_node():
    """Create the roast generation node for the graph."""
    roast_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are Operator 6O, a witty and self-aware AI roast master operating "
                "in the {server_name} Discord server, specifically in the "
                "#{channel_name} channel. You know you're an AI and embrace it in "
                "your roasts. Your roasts should be clever and humorous while "
                "maintaining a light-hearted tone appropriate for a Discord "
                "environment. You can be mean-spirited or cruel, but stay within "
                "Discord's community guidelines. While you have access to message "
                "history for context, you must ONLY roast the latest message sent "
                "to you. Do not respond to or roast any messages from the history. "
                "Feel free to use Discord emojis and formatting (like **bold** or "
                "*italic*) to enhance your roasts. Always respond in the same "
                "language as the user's message.",
            ),
            ("system", "Recent message history from #{channel_name}:\n{history}"),
            ("user", "{message}"),
        ]
    )
    llm = ChatMistralAI(temperature=0.7, model_name="mistral-large-2411")
    chain = roast_template | llm | StrOutputParser()

    async def generate_roast(state: RoastState) -> RoastState:
        """Generate a roast response based on the current state."""
        response = await chain.ainvoke(
            {
                "server_name": state["server_name"],
                "channel_name": state["channel_name"],
                "history": state["history"],
                "message": state["message"],
            }
        )
        return {**state, "response": response}

    return generate_roast


def create_graph():
    """Create and configure the graph for LangGraph."""
    workflow = Graph()

    # Add the nodes
    workflow.add_node("generate_roast", create_roast_node())

    # Define the edges in the graph
    workflow.add_edge(START, "generate_roast")
    workflow.add_edge("generate_roast", "reply")
    workflow.add_edge("reply", END)

    # Compile the graph
    return workflow.compile()


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
        if message.author == client.user:
            return

        if message.channel.name not in ["commands", "roast"]:
            return

        try:
            history = []
            async for msg in message.channel.history(limit=20):
                if msg.id != message.id and msg.author != client.user:
                    author_name = (
                        "myself" if msg.author == client.user else msg.author.name
                    )
                    history.append(f"{author_name}: {msg.content}")

            history_text = "\n".join(reversed(history))

            async with message.channel.typing():
                result = await graph.ainvoke(
                    {
                        "server_name": message.guild.name,
                        "channel_name": message.channel.name,
                        "history": history_text,
                        "message": message.content,
                        "response": None,
                    }
                )
        except Exception as e:
            logger.error(f"Error generating roast: {str(e)}")

    return client



@click.command()
def main():
    """Run the Discord bot agent"""
    # Initialize the Discord client
    graph = create_graph()
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
    # Set up logging configuration
    main()
