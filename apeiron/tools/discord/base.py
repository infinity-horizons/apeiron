from typing import Any

from langchain_core.tools.base import BaseTool


class BaseDiscordTool(BaseTool):
    """Base class for Discord tools."""

    client: Any = None  #: :meta private:

    def _run(self) -> list[dict]:
        raise NotImplementedError(
            "Synchronous operations are not supported. Use async methods instead."
        )
