from fastapi import FastAPI, HTTPException, Request, Depends, Header, Body
from discord_interactions import verify_key, InteractionResponseType
from typing import Annotated
import os
from pydantic import BaseModel, Field
import logging


# Get Discord public key from environment variable
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")


app = FastAPI(title="Apeiron Discord Webhook API")
logger = logging.getLogger(__name__)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


def verify_discord_key(
    x_signature_ed25519=Annotated[str, Header()],
    x_signature_timestamp=Annotated[str, Header()],
    body=Annotated[bytes, Body()],
):
    """
    Verify the request is from Discord
    """
    logger.debug("Verifying Discord signature %s", x_signature_ed25519)
    if not verify_key(
        body, x_signature_ed25519, x_signature_timestamp, DISCORD_PUBLIC_KEY
    ):
        raise HTTPException(status_code=401, detail="Invalid request signature")


class DiscordInteraction(BaseModel):
    type: int = Field(..., description="Type of interaction")
    data: dict = Field(..., description="Data of interaction")


@app.post("/webhooks/discord", dependencies=[Depends(verify_discord_key)])
async def webhook_discord(
    request: Request, body: Annotated[DiscordInteraction, Body(embed=True)]
):
    """
    Receive Discord webhook
    """
    body = await request.json()
    logger.info("Received Discord webhook request for type: %s", body.get("type"))
    match body.get("type"):
        case InteractionResponseType.PING:
            return {"type": InteractionResponseType.PONG}
        case _:
            raise HTTPException(status_code=400, detail="Invalid request type")
