import logging

from fastapi import FastAPI

from . import discord, github

logging.basicConfig(level=logging.DEBUG)


app = FastAPI(title="Apeiron Discord Webhook API")
logger = logging.getLogger(__name__)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(
    discord.router,
    tags=["discord"],
)

app.include_router(
    github.router,
    tags=["github"],
)
