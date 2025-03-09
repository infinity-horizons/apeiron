from functools import cache

from langchain_mistralai.chat_models import ChatMistralAI
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer


@cache
def get_tokenizer(model_name: str) -> MistralTokenizer:
    """Get the tokenizer for a given model."""
    return MistralTokenizer.from_model(model_name, strict=True)


def create_chat_model(model_name: str, **kwargs) -> ChatMistralAI:
    """Create a MistralAI chat model."""
    tokenizer = get_tokenizer(model_name)

    def _get_token_ids(text: str) -> list[int]:
        return tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=False, eos=False)

    return ChatMistralAI(
        model_name=model_name, custom_get_token_ids=_get_token_ids, **kwargs
    )
