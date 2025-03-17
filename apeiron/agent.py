import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress

import discord
import mlflow
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_core.messages import trim_messages

from .agents.operator_6o import create_agent
from .chat_message_histories.discord import DiscordChannelChatMessageHistory
from .chat_models import create_chat_model
from .toolkits.discord.toolkit import DiscordToolkit
from .tools.discord.utils import is_client_user
from .utils import (
    create_logging_handlers,
    create_thread_id,
    get_logging_level,
    parse_feature_gates,
    trim_messages_images,
)

logger = logging.getLogger(__name__)


def create_app():
    # Intrumentalise the langchain_core with mlflow
    mlflow.langchain.autolog()

    # Get log level from environment variable, default to INFO if not set
    logging.basicConfig(level=get_logging_level(), handlers=create_logging_handlers())

    # Parse environment variables
    agent_model = os.getenv("AGENT_MODEL", "pixtral-12b-2409")
    agent_provider = os.getenv("AGENT_PROVIDER", "mistralai")
    feature_gates_str = os.getenv("FEATURE_GATES", "")
    feature_gates_dict = parse_feature_gates(feature_gates_str)

    # Initialize the MistralAI model
    model = create_chat_model(provider_name=agent_provider, model_name=agent_model)

    # Initialize the Discord client
    # Set up intents with message content and DM permissions
    intents = discord.Intents.default()
    intents.message_content = True
    intents.dm_messages = True

    bot = discord.Bot(intents=intents)
    tools = []
    if feature_gates_dict.get("AgentDiscordToolkit", False):
        tools = DiscordToolkit(client=bot).get_tools()
    graph = create_agent(tools=tools, model=model)

    # Discord message handler directly in create_app
    @bot.listen
    async def on_message(message: discord.Message):
        if is_client_user(bot, message):
            return

        # Check if message is reply to bot or contains mention
        if message.reference and message.reference.resolved:
            if message.reference.resolved.author.id != bot.user.id:
                logger.debug(f"Message not replying to bot: {message.content}")
                return
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
                result = await graph.ainvoke(
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

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Initialize bot on startup
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("DISCORD_TOKEN environment variable is not set")

        # Start the bot in the background
        bot_task = asyncio.create_task(bot.start(token))

        yield

        # Cleanup on shutdown
        await bot.close()
        bot_task.cancel()
        with suppress(asyncio.CancelledError):
            await bot_task

    app = FastAPI(lifespan=lifespan)

    @app.get("/healthz")
    async def liveness_probe():
        return {"status": "ok"}

    @app.get("/readyz")
    async def readiness_probe():
        if bot.is_ready():
            return {"status": "ready"}
        return JSONResponse(content={"status": "not ready"}, status_code=503)

    @app.get("/livez")
    async def startup_probe():
        if not bot.is_closed():
            return {"status": "ready"}
        return JSONResponse(content={"status": "starting"}, status_code=503)

    return app
