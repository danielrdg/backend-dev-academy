import os
from google.genai import Client
from google.genai import types

# 1. Carrega a chave da API Gemini/GenAI a partir do .env
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise RuntimeError("GENAI_API_KEY não definida em .env")

# 2. Instancia o client singleton
_client = Client(api_key=GENAI_API_KEY)

class GeminiClient:
    def __init__(self, default_model: str = "gemini-2.0-flash"):
        self.default_model = default_model
        self.client = _client

    def generate(self, prompt: str, model: str = None) -> str:
        """
        Envia o prompt ao modelo Gemini/GenAI e retorna o texto da primeira resposta.
        """
        chosen_model = model or self.default_model

        # Cria um Part contendo o texto do usuário
        part = types.Part.from_text(text=prompt)

        # Faz a chamada síncrona para gerar conteúdo
        response = self.client.models.generate_content(
            model=chosen_model,
            contents=[part],
        )

        # Extrai a primeira "candidate" gerada
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return ""

        first = candidates[0]
        # dependendo da versão da lib, o campo da resposta pode ser `.content` ou `.text`
        return getattr(first, "content", None) or getattr(first, "text", "")

