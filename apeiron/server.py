from fastapi import FastAPI, HTTPException, Request, Response
from discord_interactions import verify_key
from typing import Dict, Callable, Awaitable
import uvicorn
import os

app = FastAPI(title="Apeiron Discord Webhook API")

# Get Discord public key from environment variable
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")


@app.middleware("http")
async def verify_discord_key(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = await request.body()

    if not verify_key(body, signature, timestamp, DISCORD_PUBLIC_KEY):
        raise HTTPException(status_code=401, detail="Invalid request signature")

    return call_next(request)


@app.post("/webhook/discord")
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
