import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress

from discord import AutoShardedBot, Client, Intents, Message
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import trim_messages

import apeiron.logging
from apeiron.chat_message_histories.discord import DiscordChannelChatMessageHistory
from apeiron.agents.operator_6o import create_agent
from apeiron.chat_models import create_chat_model
from apeiron.store import create_store
from apeiron.toolkits.discord.toolkit import DiscordToolkit
from apeiron.tools.discord.utils import (
    create_chat_message,
    create_configurable,
    is_bot_mentioned,
    is_bot_message,
    is_private_channel,
)
from apeiron.messages.utils import trim_messages_images

logger = logging.getLogger(__name__)


def create_bot():
    # Initialize the MistralAI model
    chat_model = create_chat_model(
        model=os.getenv("APEIRON_MODEL", "mistralai:pixtral-large-2411")
    )
    store = create_store(
        model=os.getenv("APEIRON_EMBEDDING", "mistralai:mistral-embed"),
    )

    # Initialize the Discord client
    bot = AutoShardedBot(intents=Intents.all())
    tools = DiscordToolkit(client=bot).get_tools()
    graph = create_agent(tools=tools, model=chat_model, store=store)

    # Discord message handler directly in create_app
    @bot.listen
    async def on_message(message: Message):
        if is_bot_message(bot, message):
            return

        if not is_bot_mentioned(bot, message) and not is_private_channel(message):
            logger.debug(
                f"Message from {message.author.name} in {message.channel.name} "
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
            config: RunnableConfig = {
                "configurable": create_configurable(message),
            }
            if message.guild:
                config["configurable"]["guild_id"] = message.guild.id
            async with message.channel.typing():
                result = await graph.ainvoke(
                    {"messages": messages},
                    config=config,
                )
            await message.channel.send(result["messages"][-1].content)

        except Exception as e:
            logger.error(f"Error handling message event: {str(e)}")

    return bot


def create_api_lifespan(bot: Client):
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

    return lifespan


def create_api(bot: Client):
    app = FastAPI(lifespan=create_api_lifespan(bot))

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
            return {"status": "live"}
        return JSONResponse(content={"status": "not live"}, status_code=503)

    return app


def create_app():
    apeiron.logging.init()
    return create_api(create_bot())
