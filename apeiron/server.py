from fastapi import FastAPI, HTTPException, Request, Depends, Header, Body
from discord_interactions import verify_key, InteractionResponseType
from typing import Annotated
import os
from pydantic import BaseModel, Field
import hmac
import hashlib
import logging


DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

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


def verify_github_signature(
    x_hub_signature_256=Annotated[str | None, Header(alias="X-Hub-Signature-256")],
    body=Annotated[bytes, Body()],
):
    """
    Verify the request is from GitHub
    """
    if not GITHUB_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500, detail="GitHub webhook secret not configured"
        )

    if not x_hub_signature_256:
        raise HTTPException(status_code=401, detail="No signature header")

    expected_signature = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(), msg=body, digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={expected_signature}", x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")


class GitHubWebhook(BaseModel):
    event: str = Field(..., description="GitHub event type")
    payload: dict = Field(..., description="GitHub event payload")


@app.post("/webhooks/github", dependencies=[Depends(verify_github_signature)])
async def webhook_github(
    request: Request,
    x_github_event: Annotated[str, Header(alias="X-GitHub-Event")],
):
    """
    Receive GitHub webhook
    """
    body = await request.json()
    return {"status": "received", "event": x_github_event, "payload": body}
