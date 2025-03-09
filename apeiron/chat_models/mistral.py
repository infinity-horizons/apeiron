from langchain_mistralai.chat_models import ChatMistralAI
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer

def get_token_ids(token: str) -> list[int]:
    """Get the token ids from the tokenizer."""
    tokenizer = MistralTokenizer.from_model("nemostral")
    return tokenizer.encode(token).ids


def get_model(model_name: str) -> ChatMistralAI:
    """Get the ChatMistralAI model."""
    return ChatMistralAI(model_name=model_name, custom_get_token_ids=get_token_ids)
