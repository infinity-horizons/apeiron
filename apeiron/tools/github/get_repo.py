from pydantic import BaseModel, Field

from apeiron.tools.github.base import BaseGithubTool


class GetRepoInput(BaseModel):
    """Input for getting repository details."""

    repository: str = Field(
        description="The repository name or full name (owner/repo) to get details for.",
    )


class GitHubGetRepoTool(BaseGithubTool):
    """Tool for getting GitHub repository details."""

    name: str = "github_get_repo"
    description: str = "Get detailed information about a GitHub repository."
    args_schema: type[GetRepoInput] = GetRepoInput

    async def _arun(
        self,
        repository: str,
    ) -> dict:
        """Get GitHub repository details asynchronously.

        Args:
            repository: The repository name or full name to get details for.

        Returns:
            Detailed information about the repository.
        """
        # Handle both repository name and full name formats
        if "/" not in repository:
            repository = f"{self.client.get_user().login}/{repository}"

        repo = self.client.get_repo(repository)
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description,
            "private": repo.private,
            "url": repo.html_url,
            "default_branch": repo.default_branch,
            "language": repo.language,
            "forks_count": repo.forks_count,
            "stargazers_count": repo.stargazers_count,
            "open_issues_count": repo.open_issues.totalCount,
        }
