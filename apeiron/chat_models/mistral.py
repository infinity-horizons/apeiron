from langchain_mistralai.chat_models import ChatMistralAI as BaseChatMistralAI
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer


class ChatMistralAI(BaseChatMistralAI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tokenizer = MistralTokenizer.v3(is_tekken=True)

    def get_token_ids(self, token: str) -> list[int]:
        """Get the token ids from the tokenizer."""
        return self.tokenizer.encode(token).ids
