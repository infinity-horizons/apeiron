from langchain_core.language_models import BaseChatModel

from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

from apeiron.chat_models.mistral import create_chat_model as create_chat_model_mistral


def create_chat_model(provider_name: str, model_name: str, **kwargs) -> BaseChatModel:
    """Initialize the agent model based on the provider and model name."""
    match provider_name:
        case "mistralai":
            return create_chat_model_mistral(model_name=model_name, **kwargs)
        case "google-ai":
            return ChatGoogleGenerativeAI(model=model_name, **kwargs)
        case _:
            raise ValueError(f"Invalid agent provider: {provider_name}")
