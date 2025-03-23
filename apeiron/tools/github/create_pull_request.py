from pydantic import BaseModel, Field

from apeiron.tools.github.base import BaseGithubTool


class CreatePullRequestInput(BaseModel):
    """Input for creating a pull request."""

    repository: str = Field(
        description="The repository name or full name (owner/repo) to create the pull request in.",
    )
    title: str = Field(
        description="The title of the pull request.",
    )
    body: str = Field(
        description="The description of the pull request.",
    )
    head: str = Field(
        description="The name of the branch where your changes are implemented.",
    )
    base: str = Field(
        default="main",
        description="The name of the branch you want the changes pulled into.",
    )
    draft: bool = Field(
        default=False,
        description="Whether to create the pull request as a draft.",
    )
    reviewers: list[str] | None = Field(
        default=None,
        description="GitHub usernames to request reviews from.",
    )


class GitHubCreatePullRequestTool(BaseGithubTool):
    """Tool for creating GitHub pull requests."""

    name: str = "github_create_pull_request"
    description: str = "Create a new pull request in a GitHub repository."
    args_schema: type[CreatePullRequestInput] = CreatePullRequestInput

    async def _arun(
        self,
        repository: str,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False,
        reviewers: list[str] | None = None,
    ) -> dict:
        """Create a GitHub pull request asynchronously.

        Args:
            repository: The repository name or full name to create the pull request in.
            title: The title of the pull request.
            body: The description of the pull request.
            head: The name of the branch where your changes are implemented.
            base: The name of the branch you want the changes pulled into.
            draft: Whether to create the pull request as a draft.
            reviewers: GitHub usernames to request reviews from.

        Returns:
            The created pull request's number and URL.
        """
        # Handle both repository name and full name formats
        if "/" not in repository:
            repository = f"{self.client.get_user().login}/{repository}"

        repo = self.client.get_repo(repository)
        pr = repo.create_pull(
            title=title,
            body=body,
            head=head,
            base=base,
            draft=draft,
        )

        if reviewers:
            pr.create_review_request(reviewers=reviewers)

        return {
            "number": pr.number,
            "url": pr.html_url,
        }
