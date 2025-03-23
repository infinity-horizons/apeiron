from typing import Any

from pydantic import BaseModel, Field

from apeiron.tools.github.base import BaseGithubTool


class ListReposInput(BaseModel):
    """Input for listing repositories."""

    visibility: str = Field(
        default="all",
        description="Filter repositories by visibility (all, public, private).",
    )


class ListReposOutput(BaseModel):
    """Output for listing repositories."""

    repositories: list[dict[str, Any]] = Field(
        description="List of repositories with their details.",
    )


class GitHubListReposTool(BaseGithubTool):
    """Tool for listing GitHub repositories."""

    name: str = "github_list_repos"
    description: str = "List GitHub repositories for the authenticated user."
    args_schema: type[ListReposInput] = ListReposInput

    async def _arun(
        self,
        visibility: str = "all",
    ) -> ListReposOutput:
        """List GitHub repositories asynchronously.

        Args:
            visibility: Filter repositories by visibility (all, public, private).

        Returns:
            List of repositories with their details.
        """
        repos = []
        for repo in self.client.get_user().get_repos(visibility=visibility):
            repos.append(
                {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "private": repo.private,
                    "url": repo.html_url,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat(),
                    "language": repo.language,
                    "forks_count": repo.forks_count,
                    "stargazers_count": repo.stargazers_count,
                }
            )
        return ListReposOutput(repositories=repos)
