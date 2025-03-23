from github import Github
from langchain_core.tools.base import BaseTool
from pydantic import Field


class BaseGithubTool(BaseTool):
    """Base class for GitHub tools."""

    client: Github = Field(
        exclude=True,
        repr=False,
        description="GitHub client.",
    )  #: :meta private:

    def _run(self) -> list[dict]:
        raise NotImplementedError(
            "Synchronous operations are not supported. Use async methods instead."
        )
