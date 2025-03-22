import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress

from discord import AutoShardedBot, Client, Guild, Intents, Message
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_core.runnables import RunnableConfig

import apeiron.logging
from apeiron.agents.operator_6o import Response, create_agent
from apeiron.chat_models import create_chat_model
from apeiron.toolkits.discord.toolkit import DiscordToolkit
from apeiron.tools.discord.utils import (
    create_configurable_from_guild,
    create_configurable_from_message,
    create_guild_joined_chat_message,
    create_message_received_chat_message,
    is_bot_mentioned,
    is_bot_message,
    is_private_channel,
)

logger = logging.getLogger(__name__)


def create_bot():
    # Initialize the MistralAI model
    agent_model = os.getenv("AGENT_MODEL", "pixtral-12b-2409")
    agent_provider = os.getenv("AGENT_PROVIDER", "mistralai")
    model = create_chat_model(provider_name=agent_provider, model_name=agent_model)

    # Initialize the Discord client
    bot = AutoShardedBot(intents=Intents.all())
    tools = DiscordToolkit(client=bot).get_tools()
    graph = create_agent(tools=tools, model=model)

    @bot.listen
    async def on_ready():
        logger.info(f"Logged in as {bot.user.name}")

    @bot.listen
    async def on_guild_join(guild: Guild):
        try:
            config: RunnableConfig = {
                "configurable": create_configurable_from_guild(guild),
            }
            result = await graph.ainvoke(
                {"messages": [create_guild_joined_chat_message(guild)]},
                config=config,
            )
            response: Response = result["structured_response"]

            match response.type:
                case "send":
                    if guild.system_channel:
                        await guild.system_channel.send(content=response.content)
                case "noop":
                    logger.debug("No action needed")
                case _:
                    logger.warning("Unknown response type: %s", response.type)

        except Exception as e:
            logger.error(f"Error handling guild join event: {str(e)}")

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
            config: RunnableConfig = {
                "configurable": create_configurable_from_message(message),
            }
            if message.guild:
                config["configurable"]["guild_id"] = message.guild.id
            async with message.channel.typing():
                result = await graph.ainvoke(
                    {"messages": [create_message_received_chat_message(message)]},
                    config=config,
                )
            response: Response = result["structured_response"]

            match response.type:
                case "send":
                    await message.channel.send(content=response.content)
                case "reply":
                    await message.reply(content=response.content)
                case "noop":
                    logger.debug("No action needed")
                case _:
                    logger.warning("Unknown response type: %s", response.type)

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
