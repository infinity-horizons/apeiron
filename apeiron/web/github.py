import hashlib
import hmac
import logging
from datetime import datetime
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel

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
    description: str | None = None
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
    language: str | None = None
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
    added: list[str]
    removed: list[str]
    modified: list[str]


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
    base_ref: str | None = None
    compare: str
    commits: list[GitHubCommit]
    head_commit: GitHubCommit | None = None


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
    labels: list[dict]
    state: str
    locked: bool
    assignee: GitHubUser | None = None
    assignees: list[GitHubUser]
    milestone: dict | None = None
    comments: int
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    body: str | None = None


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
    body: str | None = None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None
    merged_at: datetime | None = None
    merge_commit_sha: str | None = None
    assignee: GitHubUser | None = None
    assignees: list[GitHubUser]
    requested_reviewers: list[GitHubUser]
    requested_teams: list[dict]
    labels: list[dict]
    milestone: dict | None = None
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
    auto_merge: dict | None = None
    active_lock_reason: str | None = None


class GitHubPullRequestEvent(BaseModel):
    action: str
    number: int
    pull_request: GitHubPullRequest
    repository: GitHubRepository
    sender: GitHubUser


def create_router(secret: str):
    if not secret:
        raise ValueError("GitHub webhook secret not configured")

    router = APIRouter()

    async def verify_github_signature(
        request: Request,
        x_hub_signature_256: Annotated[str | None, Header()],
    ):
        """
        Verify the request is from GitHub
        """
        if not x_hub_signature_256:
            raise HTTPException(status_code=401, detail="No signature header")
        expected_signature = hmac.new(
            secret.encode(),
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

    return router
