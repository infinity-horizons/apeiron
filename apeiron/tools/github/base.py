from github import GithubIntegration
from langchain_core.tools.base import BaseTool
from pydantic import Field


class BaseGithubTool(BaseTool):
    """Base class for GitHub tools."""

    client: GithubIntegration = Field(
        exclude=True,
        repr=False,
        description="GitHub Integration client for GitHub App authentication.",
    )  #: :meta private:

    def _run(self) -> list[dict]:
        raise NotImplementedError(
            "Synchronous operations are not supported. Use async methods instead."
        )
