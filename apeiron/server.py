from fastapi import FastAPI, HTTPException, Request
from discord_interactions import verify_key_decorator
from typing import Dict
import uvicorn
import os

app = FastAPI(title="Apeiron Discord Webhook API")

# Get Discord public key from environment variable
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")


@app.post("/webhook/discord")
@verify_key_decorator(DISCORD_PUBLIC_KEY)
async def handle_discord_webhook(request: Request):
    try:
        interaction_data = await request.json()
        # Process the Discord interaction data
        # This could be a command, component interaction, etc.

        return {
            "type": 1  # Type 1 is PONG for Discord interactions
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process webhook: {str(e)}"
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
