from langchain_core.chat_models import BaseChatModel

from .mistral import create_chat_model as create_chat_model_mistral


def create_chat_model(provider_name: str, model_name: str, **kwargs) -> BaseChatModel:
    """Initialize the agent model based on the provider and model name."""
    if provider_name == "mistralai":
        return create_chat_model_mistral(model_name=model_name, **kwargs)
    else:
        raise ValueError(f"Invalid agent provider: {provider_name}")
