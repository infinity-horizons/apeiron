from typing import Self

from langchain_mistralai.chat_models import ChatMistralAI as BaseChatMistralAI
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from pydantic import Field, model_validator


class ChatMistralAI(BaseChatMistralAI):
    tokenizer: MistralTokenizer = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validate that tokenizer exists in environment."""
        try:
            if self.tokenizer is None:
                self.tokenizer = MistralTokenizer.v3(is_tekken=True)
        except ImportError as e:
            raise ValueError(
                "Could not import mistral tokenizer python package. "
                "Please install it with `pip install mistral-tokenizer`."
            ) from e
        return self

    def get_token_ids(self, token: str) -> list[int]:
        """Get the token ids from the tokenizer."""
        return self.tokenizer.encode(token).ids
