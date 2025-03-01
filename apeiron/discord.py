import logging
import os
from enum import IntEnum
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from pydantic import BaseModel, Field

DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")

router = APIRouter()
logger = logging.getLogger(__name__)


async def verify_discord_key(
    request: Request,
    x_signature_ed25519: Annotated[str | None, Header()] = None,
    x_signature_timestamp: Annotated[str | None, Header()] = None,
):
    """
    Verify the request is from Discord using Ed25519 signature
    """
    if x_signature_ed25519 is None or x_signature_timestamp is None:
        logger.error("Missing required signature headers")
        raise HTTPException(
            status_code=400, detail="Missing required signature headers"
        )
    logger.debug("Verifying Discord signature %s", x_signature_ed25519)
    if not DISCORD_PUBLIC_KEY:
        raise HTTPException(status_code=500, detail="Discord public key not configured")
    try:
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        message = x_signature_timestamp.encode() + await request.body()
        verify_key.verify(message, bytes.fromhex(x_signature_ed25519))
    except (ValueError, BadSignatureError) as e:
        logger.error("Failed to verify Discord signature: %s", str(e))
        raise HTTPException(status_code=401, detail="Invalid request signature") from e


class DiscordInteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3
    APPLICATION_COMMAND_AUTOCOMPLETE = 4
    MODAL_SUBMIT = 5


class DiscordInteractionResponseType(IntEnum):
    PONG = 1
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9


class DiscordUser(BaseModel):
    id: str
    username: str
    discriminator: str
    global_name: str | None = None
    avatar: str | None = None
    bot: bool | None = None
    system: bool | None = None
    mfa_enabled: bool | None = None
    locale: str | None = None
    verified: bool | None = None
    email: str | None = None
    flags: int | None = None
    premium_type: int | None = None
    public_flags: int | None = None


class DiscordMember(BaseModel):
    user: DiscordUser | None = None
    nick: str | None = None
    avatar: str | None = None
    roles: list[str] = Field(default_factory=list)
    joined_at: str
    premium_since: str | None = None
    deaf: bool
    mute: bool
    flags: int
    pending: bool | None = None
    permissions: str | None = None
    communication_disabled_until: str | None = None


class DiscordMessageAttachment(BaseModel):
    id: str
    filename: str
    description: str | None = None
    content_type: str | None = None
    size: int
    url: str
    proxy_url: str
    height: int | None = None
    width: int | None = None
    ephemeral: bool | None = None


class DiscordEmbed(BaseModel):
    title: str | None = None
    type: str | None = None
    description: str | None = None
    url: str | None = None
    timestamp: str | None = None
    color: int | None = None
    footer: dict | None = None
    image: dict | None = None
    thumbnail: dict | None = None
    video: dict | None = None
    provider: dict | None = None
    author: dict | None = None
    fields: list[dict] = Field(default_factory=list)


class DiscordMessage(BaseModel):
    id: str
    channel_id: str
    author: DiscordUser
    content: str
    timestamp: str
    edited_timestamp: str | None = None
    tts: bool
    mention_everyone: bool
    mentions: list[DiscordUser] = Field(default_factory=list)
    mention_roles: list[str] = Field(default_factory=list)
    mention_channels: list[dict] | None = None
    attachments: list[DiscordMessageAttachment] = Field(default_factory=list)
    embeds: list[DiscordEmbed] = Field(default_factory=list)
    reactions: list[dict] | None = None
    nonce: str | None = None
    pinned: bool
    webhook_id: str | None = None
    type: int
    activity: dict | None = None
    application: dict | None = None
    application_id: str | None = None
    message_reference: dict | None = None
    flags: int | None = None
    referenced_message: Optional["DiscordMessage"] = None
    interaction: dict | None = None
    thread: dict | None = None
    components: list[dict] | None = None
    sticker_items: list[dict] | None = None


class DiscordInteractionData(BaseModel):
    id: str
    name: str
    type: int
    resolved: dict | None = None
    options: list[dict] | None = None
    guild_id: str | None = None
    target_id: str | None = None
    custom_id: str | None = None
    component_type: int | None = None
    values: list[str] | None = None
    components: list[dict] | None = None


class DiscordInteraction(BaseModel):
    id: str
    application_id: str
    type: DiscordInteractionType
    data: DiscordInteractionData | None = None
    guild_id: str | None = None
    channel_id: str | None = None
    member: DiscordMember | None = None
    user: DiscordUser | None = None
    token: str
    version: int
    message: DiscordMessage | None = None
    app_permissions: str | None = None
    locale: str | None = None
    guild_locale: str | None = None


@router.post("/webhooks/discord", dependencies=[Depends(verify_discord_key)])
async def webhook_discord_interactions(interaction: DiscordInteraction):
    """
    Receive Discord webhook
    """
    logger.debug("Received Discord webhook request for type: %s", interaction.type)
    match interaction.type:
        case DiscordInteractionType.PING:
            return {"type": DiscordInteractionResponseType.PONG}
        case _:
            raise HTTPException(status_code=400, detail="Invalid request type")
