import hashlib
import hmac
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Annotated, List, Optional

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field

GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")

router = APIRouter()
logger = logging.getLogger(__name__)


class GitHubEventType(str, Enum):
    PING = "ping"
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"
    RELEASE = "release"
    CREATE = "create"
    DELETE = "delete"
    FORK = "fork"
    STAR = "star"
    WATCH = "watch"


class GitHubUser(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str = ""
    url: str
    html_url: str
    type: str
    site_admin: bool


class GitHubRepository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: GitHubUser
    html_url: str
    description: Optional[str] = None
    fork: bool
    url: str
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime
    git_url: str
    ssh_url: str
    clone_url: str
    size: int
    stargazers_count: int
    watchers_count: int
    language: Optional[str] = None
    has_issues: bool
    has_projects: bool
    has_downloads: bool
    has_wiki: bool
    has_pages: bool
    has_discussions: bool
    forks_count: int
    archived: bool
    disabled: bool
    open_issues_count: int
    default_branch: str


class GitHubPingEvent(BaseModel):
    zen: str
    hook_id: int
    hook: dict
    repository: GitHubRepository
    sender: GitHubUser


class GitHubCommit(BaseModel):
    id: str
    tree_id: str
    distinct: bool
    message: str
    timestamp: datetime
    url: str
    author: dict
    committer: dict
    added: List[str]
    removed: List[str]
    modified: List[str]


class GitHubPushEvent(BaseModel):
    ref: str
    before: str
    after: str
    repository: GitHubRepository
    pusher: dict
    sender: GitHubUser
    created: bool
    deleted: bool
    forced: bool
    base_ref: Optional[str] = None
    compare: str
    commits: List[GitHubCommit]
    head_commit: Optional[GitHubCommit] = None


class GitHubIssue(BaseModel):
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    id: int
    node_id: str
    number: int
    title: str
    user: GitHubUser
    labels: List[dict]
    state: str
    locked: bool
    assignee: Optional[GitHubUser] = None
    assignees: List[GitHubUser]
    milestone: Optional[dict] = None
    comments: int
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    body: Optional[str] = None


class GitHubIssueEvent(BaseModel):
    action: str
    issue: GitHubIssue
    repository: GitHubRepository
    sender: GitHubUser


class GitHubPullRequest(BaseModel):
    url: str
    id: int
    node_id: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: GitHubUser
    body: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    merge_commit_sha: Optional[str] = None
    assignee: Optional[GitHubUser] = None
    assignees: List[GitHubUser]
    requested_reviewers: List[GitHubUser]
    requested_teams: List[dict]
    labels: List[dict]
    milestone: Optional[dict] = None
    draft: bool
    commits_url: str
    review_comments_url: str
    review_comment_url: str
    comments_url: str
    statuses_url: str
    head: dict
    base: dict
    _links: dict
    author_association: str
    auto_merge: Optional[dict] = None
    active_lock_reason: Optional[str] = None


class GitHubPullRequestEvent(BaseModel):
    action: str
    number: int
    pull_request: GitHubPullRequest
    repository: GitHubRepository
    sender: GitHubUser


async def verify_github_signature(
    request: Request,
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
        GITHUB_WEBHOOK_SECRET.encode(),
        msg=await request.body(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(f"sha256={expected_signature}", x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")


@router.post("/webhooks/github", dependencies=[Depends(verify_github_signature)])
async def webhook_github(
    request: Request,
    x_github_event: Annotated[str | None, Header(alias="X-GitHub-Event")] = None,
):
    """
    Receive GitHub webhook
    """
    if not x_github_event:
        logger.error("Missing X-GitHub-Event header")
        raise HTTPException(status_code=400, detail="Missing event header")
    logger.debug("Received GitHub webhook request for event: %s", x_github_event)
    try:
        event_type = GitHubEventType(x_github_event)
        body = await request.json()
        match event_type:
            case GitHubEventType.PING:
                payload = GitHubPingEvent(**body)
            case GitHubEventType.PUSH:
                payload = GitHubPushEvent(**body)
            case GitHubEventType.ISSUES:
                payload = GitHubIssueEvent(**body)
            case GitHubEventType.PULL_REQUEST:
                payload = GitHubPullRequestEvent(**body)
            case _:
                logger.warning("Unhandled event type: %s", x_github_event)
                payload = body

        return {"status": "received", "event": x_github_event, "payload": payload}
    except ValueError as e:
        logger.error("Failed to parse webhook payload: %s", str(e))
        raise HTTPException(status_code=400, detail="Invalid payload format") from e
