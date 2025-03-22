from discord import Client
from langchain_core.tools.base import BaseTool
from pydantic import Field


class BaseDiscordTool(BaseTool):
    """Base class for Discord tools."""

    client: Client = Field(
        exclude=True,
        repr=False,
        description="Discord client.",
    )  #: :meta private:

    def _run(self) -> list[dict]:
        raise NotImplementedError(
            "Synchronous operations are not supported. Use async methods instead."
        )
