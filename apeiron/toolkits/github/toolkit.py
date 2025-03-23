from typing import Any

from langchain_core.tools.base import BaseTool, BaseToolkit

from apeiron.tools.github.create_issue import GitHubCreateIssueTool
from apeiron.tools.github.create_pull_request import GitHubCreatePullRequestTool
from apeiron.tools.github.get_repo import GitHubGetRepoTool
from apeiron.tools.github.list_repos import GitHubListReposTool


class GitHubToolkit(BaseToolkit):
    """Toolkit for GitHub operations."""

    client: Any = None  #: :meta private:

    def get_tools(self) -> list[BaseTool]:
        """Get the tools in the toolkit.

        Returns:
            List of GitHub tools.
        """
        return [
            GitHubCreateIssueTool(client=self.client),
            GitHubCreatePullRequestTool(client=self.client),
            GitHubGetRepoTool(client=self.client),
            GitHubListReposTool(client=self.client),
        ]
