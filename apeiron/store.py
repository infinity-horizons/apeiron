from functools import cache

from langchain.embeddings import init_embeddings
from langgraph.store.memory import InMemoryStore
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer


@cache
def get_mistral_tokenizer(model_name: str) -> MistralTokenizer:
    """Get the tokenizer for a given model."""
    return MistralTokenizer.from_model(model_name, strict=True)


def create_store(model: str, **kwargs) -> InMemoryStore:
    """Create a memory store."""
    if model.startswith("mistralai:") or kwargs.get("model_provider") == "mistralai":
        tokenizer = get_mistral_tokenizer(model.removeprefix("mistralai:"))
    else:
        tokenizer = None

    return InMemoryStore(
        index={
            "dims": 1536,
            "embed": init_embeddings(model, tokenizer=tokenizer),
            "fields": ["text"],
        }
    )
