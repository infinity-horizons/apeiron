import hashlib
import hmac
import logging
import os
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

router = APIRouter()
logger = logging.getLogger(__name__)


async def verify_github_signature(
    req: Request,
    x_hub_signature_256: Annotated[str | None, Header()],
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
        GITHUB_WEBHOOK_SECRET.encode(), msg=await req.body(), digestmod=hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(f"sha256={expected_signature}", x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")


class GitHubWebhook(BaseModel):
    event: str = Field(..., description="GitHub event type")
    payload: dict = Field(..., description="GitHub event payload")


@router.post("/webhooks/github", dependencies=[Depends(verify_github_signature)])
async def webhook_github(
    body: Annotated[GitHubWebhook, Body(embed=True)],
    x_github_event: Annotated[str | None, Header(alias="X-GitHub-Event")] = None,
):
    """
    Receive GitHub webhook
    """
    if not x_github_event:
        logger.error("Missing X-GitHub-Event header")
        raise HTTPException(status_code=400, detail="Missing event header")
    logger.info("Received GitHub webhook request for event: %s", x_github_event)
    return {"status": "received", "event": x_github_event, "payload": body}
