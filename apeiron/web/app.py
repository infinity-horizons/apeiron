import logging
import os

from fastapi import FastAPI

from . import discord, github

logging.basicConfig(level=logging.DEBUG)


app = FastAPI(title="Apeiron Webhook API")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(
    discord.create_router(os.getenv("DISCORD_PUBLIC_KEY")),
    tags=["discord"],
)

app.include_router(
    github.create_router(os.getenv("GITHUB_WEBHOOK_SECRET")),
    tags=["github"],
)
