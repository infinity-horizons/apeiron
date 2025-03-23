from pydantic import BaseModel, Field

from apeiron.tools.github.base import BaseGithubTool


class CreateIssueInput(BaseModel):
    """Input for creating an issue."""

    repository: str = Field(
        description="The repository name (owner/repo) where the issue will be created.",
    )
    title: str = Field(
        description="The title of the issue.",
    )
    body: str = Field(
        description="The body text of the issue.",
    )
    labels: list[str] | None = Field(
        default=None,
        description="Labels to apply to the issue.",
    )
    assignees: list[str] | None = Field(
        default=None,
        description="GitHub usernames to assign to the issue.",
    )


class GitHubCreateIssueTool(BaseGithubTool):
    """Tool for creating GitHub issues."""

    name: str = "github_create_issue"
    description: str = "Create a new issue in a GitHub repository."
    args_schema: type[CreateIssueInput] = CreateIssueInput

    async def _arun(
        self,
        repository: str,
        title: str,
        body: str,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> dict:
        """Create a GitHub issue asynchronously.

        Args:
            repository: The repository name or full name to create the issue in.
            title: The title of the issue.
            body: The body text of the issue.
            labels: Labels to apply to the issue.
            assignees: GitHub usernames to assign to the issue.

        Returns:
            The created issue's number and URL.
        """
        repo = self.client.get_repo(repository)
        issue = repo.create_issue(
            title=title,
            body=body,
            labels=labels,
            assignees=assignees,
        )
        return {
            "number": issue.number,
            "url": issue.html_url,
        }
