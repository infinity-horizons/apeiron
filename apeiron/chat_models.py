from collections.abc import Callable
from functools import cache

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer


@cache
def get_mistral_tokenizer(model_name: str) -> MistralTokenizer:
    """Get the tokenizer for a given model."""
    return MistralTokenizer.from_model(model_name, strict=True)


def create_mistral_get_token_ids(model: str, **kwargs) -> Callable[[str], list[int]]:
    """Create a MistralAI chat model."""
    tokenizer = get_mistral_tokenizer(model)

    def _get_token_ids(text: str) -> list[int]:
        return tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=False, eos=False)

    return _get_token_ids


def create_chat_model(model: str, **kwargs) -> BaseChatModel:
    """Initialize the agent model based on the provider and model name."""
    if (
        model.startswith("mistralai")
        or kwargs.get("model_provider") == "mistralai"
        and "custom_get_token_ids" not in kwargs
    ):
        kwargs["custom_get_token_ids"] = create_mistral_get_token_ids(
            model.removeprefix("mistralai:")
        )
    return init_chat_model(model, **kwargs)
