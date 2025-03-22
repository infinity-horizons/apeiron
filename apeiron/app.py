import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress

import discord
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import apeiron.logging
from apeiron.agents.operator_6o import Response, create_agent
from apeiron.chat_models import create_chat_model
from apeiron.toolkits.discord.toolkit import DiscordToolkit
from apeiron.tools.discord.utils import (
    create_chat_message,
    create_thread_id,
    is_bot_mentioned,
    is_bot_message,
    is_private_channel,
)
from apeiron.utils import parse_feature_gates

logger = logging.getLogger(__name__)


def create_app():
    apeiron.logging.init()

    # Parse environment variables
    agent_model = os.getenv("AGENT_MODEL", "pixtral-12b-2409")
    agent_provider = os.getenv("AGENT_PROVIDER", "mistralai")
    feature_gates_str = os.getenv("FEATURE_GATES", "")
    _feature_gates_dict = parse_feature_gates(feature_gates_str)

    # Initialize the MistralAI model
    model = create_chat_model(provider_name=agent_provider, model_name=agent_model)

    # Initialize the Discord client
    bot = discord.AutoShardedBot(intents=discord.Intents.all())
    tools = DiscordToolkit(client=bot).get_tools()
    graph = create_agent(tools=tools, model=model)

    # Discord message handler directly in create_app
    @bot.listen
    async def on_message(message: discord.Message):
        if is_bot_message(bot, message):
            return

        if not is_bot_mentioned(bot, message) and not is_private_channel(message):
            logger.debug(
                f"Message from {message.author.name} in {message.channel.name} "
            )
            return

        try:
            messages = [create_chat_message(message)]
            async with message.channel.typing():
                result = await graph.ainvoke(
                    {"messages": messages},
                    config={
                        "configurable": {
                            "thread_id": create_thread_id(message),
                        }
                    },
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
            return {"status": "live"}
        return JSONResponse(content={"status": "not live"}, status_code=503)

    return app
