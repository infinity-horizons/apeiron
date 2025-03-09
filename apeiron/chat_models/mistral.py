from langchain_mistralai.chat_models import ChatMistralAI
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer

def get_token_ids(token: str) -> list[int]:
    tokenizer = MistralTokenizer.from_model("nemostral")
    return tokenizer.encode(token).ids


def get_model(agent_provider: str, agent_model: str) -> BaseChatModel:
    """Initialize the agent model based on the provider and model name."""
    return ChatMistralAI(model_name=agent_model, custom_get_token_ids=get_token_ids)
