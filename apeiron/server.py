from fastapi import FastAPI, HTTPException, Request, Response, APIRouter
from discord_interactions import verify_key, InteractionResponseType
from typing import Dict, Callable, Awaitable
import uvicorn
import os

app = FastAPI(title="Apeiron Discord Webhook API")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Get Discord public key from environment variable
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")


# Create a router for Discord webhook endpoints
discord_router = APIRouter()


@discord_router.middleware("http")
async def verify_discord_key(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    body = await request.body()

    if not verify_key(body, signature, timestamp, DISCORD_PUBLIC_KEY):
        raise HTTPException(status_code=401, detail="Invalid request signature")

    return await call_next(request)


@discord_router.post("/webhook/discord")
async def handle_discord_webhook(request: Request):
    body = await request.json()
    match body.get("type"):
        case InteractionResponseType.PING:
            return {"type": InteractionResponseType.PONG}
        case _:
            raise HTTPException(status_code=400, detail="Invalid request type")


# Include the Discord router
app.include_router(discord_router)
